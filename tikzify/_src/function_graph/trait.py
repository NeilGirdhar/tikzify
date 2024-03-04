__all__ = ['GraphedTrait']


class GraphedTrait:

    def __init__(self,
                 legend_text: str,
                 scale: float = 1.0):
        super().__init__()
        self.legend_text = legend_text
        self.scale = scale
