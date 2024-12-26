from io import BytesIO
from optimum.intel.openvino.modeling_diffusion import OVStableDiffusionPipeline
from PIL import Image


class Txt2Img:
    def __init__(self):
        """Initialize the Txt2Img class by loading the pipeline."""
        self.pipeline = self._initialize_pipeline()

    def _initialize_pipeline(self):
        """
        Load the OpenVINO Stable Diffusion pipeline with the pre-trained model.
        Returns:
            An instance of the initialized pipeline.
        """
        return OVStableDiffusionPipeline.from_pretrained(
            "rupeshs/sdxs-512-0.9-openvino",
            ov_config={"CACHE_DIR": ""},
        )

    def generate_image(self, prompt: str) -> bytes:
        """
        Generate an image from the given text prompt using the pipeline.

        Args:
            prompt (str): The text prompt to generate an image for.

        Returns:
            bytes: Binary image data in PNG format.
        """
        result = self.pipeline(
            prompt=prompt,
            width=512,
            height=512,
            num_inference_steps=1,
            guidance_scale=1,
        )

        # Convert the generated PIL image to binary data
        image = result.images[0]
        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")
        return image_bytes.getvalue()
