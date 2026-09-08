    @torch.no_grad()
    def predict(
        self,
        inputs: TensorOrArray
        | Sequence[TensorOrArray]
        | Sequence[Mapping[str, TensorOrArray | Mapping[str, TensorOrArray]]]
        | Sequence[PreparedInput],
        prediction_length: int | None = None,
        batch_size: int = 256,
        context_length: int | None = None,
        cross_learning: bool = False,
        limit_prediction_length: bool = False,
        **kwargs,
    ) -> list[torch.Tensor]:
        """
        Generate forecasts for the given time series.

        Parameters
        ----------
        inputs
            The time series to generate forecasts for, can be one of:
            - A 3-dimensional `torch.Tensor` or `np.ndarray` of shape (batch, n_variates, history_length). When `n_variates > 1`, information
            will be shared among the different variates of each time series in the batch and the model will perform multivariate forecasting.
            - A list of `torch.Tensor` or `np.ndarray` where each element can either be 1-dimensional of shape (history_length,)
            or 2-dimensional of shape (n_variates, history_length). The history_lengths may be different across elements; left-padding
            will be applied, if needed. The model will perform univariate and multivariate inference for 1-d and 2-d elements, respectively.
            A mixture of 1-d and 2-d elements can be provided in the same list.
            - A list of dictionaries where each dictionary may have the following keys.
                1. `target` (required): a 1-d or 2-d `torch.Tensor` or `np.ndarray` of shape (history_length,) or (n_variates, history_length).
                Forecasts will be generated for items in `target`.
                2. `past_covariates` (optional): a dict of past-only covariates or past values of known future covariates. The keys of the dict
                must be names of the covariates and values must be 1-d `torch.Tensor` or `np.ndarray` with length equal to the `history_length`
                of `target`.
                3. `future_covariates` (optional): a dict of future values of known future covariates. The keys of the dict must be names of the
                covariates and values must be 1-d `torch.Tensor` or `np.ndarray` with length equal to the `prediction_length`. All keys in
                `future_covariates` must be a subset of the keys in `past_covariates`.

              All dictionaries in the list must share the same schema: the same `target` shape (`n_variates`) and the same
              `past_covariates` / `future_covariates` keys (the `history_length` may differ across dictionaries). To forecast
              inputs with different schemas, loop over them and call the model once per schema.

            Examples:
            ```python

            # Batch of univariate time series
            inputs = torch.randn(32, 1, 100)

            # Batch of multivariate time series
            inputs = torch.randn(32, 3, 100)

            # List of univariate time series with different lengths
            inputs = [
                torch.randn(100),
                torch.randn(150),
                torch.randn(120),
            ]

            # List of dictionaries with covariates (one numeric and one categorical covariate known into the future).
            # Note: categorical covariates are only supported as numpy arrays as torch does not support str dtype.
            prediction_length = 24
            inputs = [
                {
                    "target": np.random.randn(history_length),
                    "past_covariates": {
                        "temperature": np.random.rand(history_length),
                        "weather_type": np.random.choice(["sunny", "cloudy", "rainy"], size=history_length),
                    },
                    "future_covariates": {
                        "temperature": np.random.rand(prediction_length),
                        "weather_type": np.random.choice(["sunny", "cloudy", "rainy"], size=prediction_length),
                    },
                }
                for history_length in [100, 150, 120]
            ]
            ```
        prediction_length
            The number of time steps to predict for, defaults to the model's default prediction length
        batch_size
            The batch size used for prediction. Note that the batch size here means the number of time series, including target(s) and covariates,
            which are input into the model. If your data has multiple target and/or covariates, the effective number of time series tasks in a batch
            will be lower than this value, by default 256
        context_length
            The maximum context length used during for inference, by default set to the model's default context length
        cross_learning
            If True, cross-learning is enabled, i.e., all the tasks in `inputs` will be predicted jointly and the model will share information across all inputs, by default False
            The following must be noted when using cross-learning:
            - Cross-learning doesn't always improve forecast accuracy and must be tested for individual use cases.
            - Results become dependent on batch size. Very large batch sizes may not provide benefits as they deviate from the maximum group size used during pretraining.
            For optimal results, consider using a batch size around 100 (as used in the Chronos-2 technical report).
            - Cross-learning is most helpful when individual time series have limited historical context, as the model can leverage patterns from related series in the batch.
        limit_prediction_length
            If True, an error is raised when prediction_length is greater than model's default prediction length, by default False

        Returns
        -------
        The model's predictions, a list of `torch.Tensor` where each element has shape (n_variates, n_quantiles, prediction_length) and the number of
        elements are equal to the number of target time series (univariate or multivariate) in the `inputs`.

        """
        model_prediction_length = self.model_prediction_length
        if prediction_length is None:
            prediction_length = model_prediction_length

        if kwargs.get("predict_batches_jointly") is not None:
            warnings.warn(
                "The `predict_batches_jointly` argument is deprecated and will be removed in a future version. "
                "Please use `cross_learning=True` to enable the cross-learning mode.",
                category=FutureWarning,
                stacklevel=2,
            )
            cross_learning = kwargs.pop("predict_batches_jointly")
        # The maximum number of output patches to generate in a single forward pass before the long-horizon heuristic kicks in. Note: A value larger
        # than the model's default max_output_patches may lead to degradation in forecast accuracy, defaults to a model-specific value
        max_output_patches = kwargs.pop("max_output_patches", self.max_output_patches)
        # The set of quantiles to use when making long-horizon predictions; must be a subset of the model's default quantiles. These quantiles
        # are appended to the historical context and input into the model autoregressively to generate long-horizon predictions. Note that the
        # effective batch size increases by a factor of `len(unrolled_quantiles)` when making long-horizon predictions,
        # by default [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        unrolled_quantiles = kwargs.pop("unrolled_quantiles", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
        # A callback which is called after each batch has been processed
        after_batch_callback: Callable = kwargs.pop("after_batch", lambda: None)

        if len(kwargs) > 0:
            raise TypeError(f"Unexpected keyword arguments: {list(kwargs.keys())}.")

        if not set(unrolled_quantiles).issubset(self.quantiles):
            raise ValueError(
                f"Unrolled quantiles must be a subset of the model's quantiles. "
                f"Found: {unrolled_quantiles=}, model_quantiles={self.quantiles}"
            )
        unrolled_quantiles_tensor = torch.tensor(unrolled_quantiles)

        if prediction_length > model_prediction_length:
            msg = (
                f"We recommend keeping prediction length <= {model_prediction_length}. "
                "The quality of longer predictions may degrade since the model is not optimized for it. "
            )
            if limit_prediction_length:
                msg += "You can turn off this check by setting `limit_prediction_length=False`."
                raise ValueError(msg)
            warnings.warn(msg)

        if context_length is None:
            context_length = self.model_context_length

        if context_length > self.model_context_length:
            warnings.warn(
                f"The specified context_length {context_length} is greater than the model's default context length {self.model_context_length}. "
                f"Resetting context_length to {self.model_context_length}."
            )
            context_length = self.model_context_length

        test_dataset = Chronos2Dataset(
            inputs,
            context_length=context_length,
            prediction_length=prediction_length,
            batch_size=batch_size,
            output_patch_size=self.model_output_patch_size,
            mode=DatasetMode.TEST,
        )
        test_loader = DataLoader(
            test_dataset, batch_size=None, pin_memory=self.model.device.type == "cuda", shuffle=False, drop_last=False
        )

        all_predictions: list[torch.Tensor] = []
        for batch in test_loader:
            assert batch["future_target"] is None
            batch_context = batch["context"]
            batch_group_ids = batch["group_ids"]
            batch_future_covariates = batch["future_covariates"]
            batch_target_idx_ranges = batch["target_idx_ranges"]

            if cross_learning:
                batch_group_ids = torch.zeros_like(batch_group_ids)

            batch_prediction = self._predict_batch(
                context=batch_context,
                group_ids=batch_group_ids,
                future_covariates=batch_future_covariates,
                unrolled_quantiles_tensor=unrolled_quantiles_tensor,
                prediction_length=prediction_length,
                max_output_patches=max_output_patches,
                target_idx_ranges=batch_target_idx_ranges,
            )
            all_predictions.extend(batch_prediction)
            after_batch_callback()

        return all_predictions
