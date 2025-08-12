from pathlib import Path

def read_fasta(file_path: str) -> str:
    """
    Reads a FASTA file and returns the concatenated sequence.
    Ignores header lines (lines starting with '>').
    """
    sequence = ""
    try:
        with Path(file_path).open("r") as f:
            for line in f:
                line = line.strip()
                if not line.startswith(">") and line:
                    sequence += line
    except FileNotFoundError:
        raise FileNotFoundError(f"FASTA file not found at: {file_path}")
    except Exception as e:
        raise IOError(f"Error reading FASTA file {file_path}: {e}")
    return sequence.upper() # Ensure sequence is uppercase

