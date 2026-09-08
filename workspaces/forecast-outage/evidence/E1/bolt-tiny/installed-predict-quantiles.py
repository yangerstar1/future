    def predict_quantiles(
        self,
        inputs: Union[torch.Tensor, List[torch.Tensor]],
        prediction_length: Optional[int] = None,
        quantile_levels: List[float] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
        **predict_kwargs,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Refer to the base method (``BaseChronosPipeline.predict_quantiles``).
        """
        # shape (batch_size, prediction_length, len(training_quantile_levels))
        predictions = (
            self.predict(inputs, prediction_length=prediction_length, **predict_kwargs).detach().swapaxes(1, 2)
        )

        training_quantile_levels = self.quantiles

        if set(quantile_levels).issubset(set(training_quantile_levels)):
            # no need to perform intra/extrapolation
            quantiles = predictions[..., [training_quantile_levels.index(q) for q in quantile_levels]]
        else:
            # we rely on torch for interpolating quantiles if quantiles that
            # Chronos Bolt was trained on were not provided
            if min(quantile_levels) < min(training_quantile_levels) or max(quantile_levels) > max(
                training_quantile_levels
            ):
                logger.warning(
                    f"\tQuantiles to be predicted ({quantile_levels}) are not within the range of "
                    f"quantiles that Chronos-Bolt was trained on ({training_quantile_levels}). "
                    "Quantile predictions will be set to the minimum/maximum levels at which Chronos-Bolt "
                    "was trained on. This may significantly affect the quality of the predictions."
                )

            # TODO: this is a hack that assumes the model's quantiles during training (training_quantile_levels)
            # made up an equidistant grid along the quantile dimension. i.e., they were (0.1, 0.2, ..., 0.9).
            # While this holds for official Chronos-Bolt models, this may not be true in the future, and this
            # function may have to be revised.
            augmented_predictions = torch.cat(
                [predictions[..., [0]], predictions, predictions[..., [-1]]],
                dim=-1,
            )
            quantiles = torch.quantile(
                augmented_predictions,
                q=torch.tensor(quantile_levels, dtype=augmented_predictions.dtype),
                dim=-1,
            ).permute(1, 2, 0)
        # NOTE: the median is returned as the mean here
        mean = predictions[:, :, training_quantile_levels.index(0.5)]
        return quantiles, mean
