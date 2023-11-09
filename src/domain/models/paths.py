from pydantic import BaseModel


class Paths(BaseModel):
    """
        A class  used to store all necessary paths
    """
    input_dir: str
    output_dir: str
    log_dir: str