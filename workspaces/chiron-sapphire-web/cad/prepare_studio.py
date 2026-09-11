"""Rebuild the vendored CC0 illumination, never a product photograph.
Usage: python cad/prepare_studio.py [path-to-studio_small_03_4k.exr]
Without an argument, download the public CC0 original and verify its SHA-256.
"""
import os
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'
from pathlib import Path
import hashlib, json, sys, urllib.request, tempfile
import cv2
SOURCE = 'https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/4k/studio_small_03_4k.exr'
SHA = 'fbaa5f64cdfddcf2ebbca7aee43457fac74b5f8b0f2755a65185eaa5d9f8e371'
EXPECTED = 'b5dd5b8873ca658ea57353ddf5fe384f9ddd25578ca049a5ff65b9cabb01fc9d'
out = Path('generated'); out.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='chiron-cc0-') as temp:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(temp)/'studio.exr'
    if len(sys.argv) == 1:
        request = urllib.request.Request(SOURCE, headers={'User-Agent': 'Chiron-independent-study/1.0'})
        with urllib.request.urlopen(request, timeout=120) as response:
            source.write_bytes(response.read())
    if hashlib.sha256(source.read_bytes()).hexdigest() != SHA:
        raise SystemExit('CC0 source changed; stop rather than silently substitute lighting.')
    image = cv2.imread(str(source), cv2.IMREAD_UNCHANGED)
    if image is None or image.shape != (2048, 4096, 3):
        raise SystemExit('Invalid HDR input dimensions/channels.')
    small = cv2.resize(image, (1024, 512), interpolation=cv2.INTER_AREA)
    result = out/'studio-small-03-1k.hdr'
    if not cv2.imwrite(str(result), small):
        raise SystemExit('HDR encoding failed.')
    result_hash = hashlib.sha256(result.read_bytes()).hexdigest()
    if result_hash != EXPECTED:
        raise SystemExit(f'HDR transform differs: {result_hash}; retain diagnostic and review versions.')
    (out/'STUDIO-SOURCE.json').write_text(json.dumps({
        'name':'Studio Small 03','author':'Greg Zaal / Poly Haven',
        'source':'https://polyhaven.com/a/studio_small_03','download':SOURCE,
        'license':'CC0','licenseSource':'https://polyhaven.com/license',
        'sourceSHA256':SHA,
        'transformation':'OpenCV area resampling to 1024 x 512, unchanged linear HDR radiance, Radiance RGBE serialization',
        'resultSHA256':result_hash,'resultBytes':result.stat().st_size,
        'role':'environment illumination; never product geometry or product photography'
    },indent=2)+'\n')
    print(json.dumps({'opencv':cv2.__version__,'result':str(result),'sha256':result_hash}))
