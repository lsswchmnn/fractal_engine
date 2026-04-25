import  numpy as np
#============================================================
class PostProcesser():

    def process(self, render_settings, image: np.ndarray):
        if not render_settings.post_process_enabled:
            return image
        
        img = self.apply_gamma(image, render_settings.gamma_factor)
        img = self.apply_contrast(image, render_settings.contrast_factor)

        if render_settings.inversion_enabled:
            img = self.apply_inversion(image)

        return img

    def apply_gamma(self, image: np.ndarray, gamma: float = 2.2) -> np.ndarray:
        if gamma <= 0:
            return image

        img = image.astype(np.float64) / 255.0
        img = np.power(img, 1.0 / gamma)
        img = np.clip(img * 255.0, 0, 255).astype(np.uint8)
        return img

    def apply_contrast(self, image: np.ndarray, contrast: float = 1.2) -> np.ndarray:
        img = image.astype(np.float64) / 255.0
        img = (img - 0.5) * contrast + 0.5
        img = np.clip(img, 0.0, 1.0)
        return (img * 255).astype(np.uint8)

    def apply_inversion(self, image: np.ndarray) -> np.ndarray:
        img = image.astype(np.float32) / 255.0
        img = 1.0 - img
        img = (img * 255).astype(np.uint8)
        return img
