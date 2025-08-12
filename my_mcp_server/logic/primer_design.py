from Bio.Seq import Seq
from Bio.SeqUtils import MeltingTemp as mt
from Bio.SeqUtils import gc_fraction # For GC content calculation

# Define target parameters for primer design
MIN_PRIMER_LEN = 18
MAX_PRIMER_LEN = 25
TARGET_GC_MIN = 40.0
TARGET_GC_MAX = 60.0
TARGET_TM_MIN = 58.0
TARGET_TM_MAX = 65.0

# Default concentrations for Tm calculation (in mM and nM)
DEFAULT_NA_CONC = 50.0
# DEFAULT_DNA_CONC = 250.0 # Removed as dnac parameter is no longer used

def _calculate_tm(sequence: str, Na: float = DEFAULT_NA_CONC) -> float:
    """
    Calculates the melting temperature (Tm) of a DNA sequence using the nearest-neighbor method.
    """
    # Tm_NN requires sequence to be a Biopython Seq object
    seq_obj = Seq(sequence)
    return mt.Tm_NN(seq_obj, Na=Na)

def _find_optimal_primer(
    target_sequence: str,
    is_forward: bool,
    enzyme_site: str
) -> dict:
    """
    Iteratively searches for an optimal primer sequence within the target_sequence.
    Considers length, GC content, and Tm.
    """
    best_primer_info = None
    min_deviation = float('inf')

    # Iterate through possible primer lengths
    for length in range(MIN_PRIMER_LEN, MAX_PRIMER_LEN + 1):
        if is_forward:
            # Forward primer: take from the beginning of the target_sequence
            if len(target_sequence) < length:
                continue # Not enough sequence for this length
            primer_binding_part = target_sequence[:length]
            full_primer_seq = enzyme_site + primer_binding_part
        else:
            # Reverse primer: take from the end, then reverse complement
            if len(target_sequence) < length:
                continue # Not enough sequence for this length
            primer_binding_part = Seq(target_sequence[-length:]).reverse_complement()
            full_primer_seq = enzyme_site + str(primer_binding_part)

        # Calculate metrics
        current_gc = gc_fraction(full_primer_seq) * 100 # gc_fraction returns a float between 0 and 1
        current_tm = _calculate_tm(full_primer_seq)

        # Check if criteria are met
        is_len_ok = MIN_PRIMER_LEN <= len(full_primer_seq) - len(enzyme_site) <= MAX_PRIMER_LEN
        is_gc_ok = TARGET_GC_MIN <= current_gc <= TARGET_GC_MAX
        is_tm_ok = TARGET_TM_MIN <= current_tm <= TARGET_TM_MAX

        if is_len_ok and is_gc_ok and is_tm_ok:
            # Found a perfect primer, return it immediately
            return {
                "binding_part": str(primer_binding_part),
                "full_primer": full_primer_seq,
                "length": len(full_primer_seq) - len(enzyme_site),
                "gc_content": round(current_gc, 2),
                "tm": round(current_tm, 2),
                "notes": "Optimal primer found within specified criteria."
            }
        else:
            # Calculate deviation for "best effort" if no perfect primer is found
            deviation = 0
            if not is_len_ok:
                deviation += min(abs(len(full_primer_seq) - len(enzyme_site) - MIN_PRIMER_LEN),
                                 abs(len(full_primer_seq) - len(enzyme_site) - MAX_PRIMER_LEN)) * 2 # Higher penalty for length
            if not is_gc_ok:
                deviation += min(abs(current_gc - TARGET_GC_MIN), abs(current_gc - TARGET_GC_MAX))
            if not is_tm_ok:
                deviation += min(abs(current_tm - TARGET_TM_MIN), abs(current_tm - TARGET_TM_MAX))

            if deviation < min_deviation:
                min_deviation = deviation
                best_primer_info = {
                    "binding_part": str(primer_binding_part),
                    "full_primer": full_primer_seq,
                    "length": len(full_primer_seq) - len(enzyme_site),
                    "gc_content": round(current_gc, 2),
                    "tm": round(current_tm, 2),
                    "notes": "Best effort primer found, but not all criteria met."
                }
    return best_primer_info if best_primer_info else {
        "binding_part": "", "full_primer": "", "length": 0, "gc_content": 0.0, "tm": 0.0,
        "notes": "Could not find any suitable primer within the given constraints."
    }


def design_primers_logic(cds_sequence: str, forward_enzyme_site: str, reverse_enzyme_site: str) -> dict:
    """
    Designs forward and reverse primers based on CDS sequence and restriction enzyme sites.
    Iteratively optimizes for length, GC content, and Tm.
    """
    if not cds_sequence:
        raise ValueError("Invalid CDS sequence: The provided sequence is empty.")

    # Normalize enzyme sites (ensure uppercase)
    forward_enzyme_site = forward_enzyme_site.upper()
    reverse_enzyme_site = reverse_enzyme_site.upper()

    # Design Forward Primer
    forward_primer_data = _find_optimal_primer(cds_sequence, True, forward_enzyme_site)

    # Design Reverse Primer
    # For reverse primer, the target sequence for binding is the reverse complement of the CDS end
    reverse_primer_data = _find_optimal_primer(cds_sequence, False, reverse_enzyme_site)

    return {
        "forward_primer": f"5'-{forward_primer_data['full_primer']}-3'",
        "forward_primer_details": {
            "binding_part": forward_primer_data['binding_part'],
            "length": forward_primer_data['length'],
            "gc_content": forward_primer_data['gc_content'],
            "tm": forward_primer_data['tm'],
            "notes": forward_primer_data['notes']
        },
        "reverse_primer": f"5'-{reverse_primer_data['full_primer']}-3'",
        "reverse_primer_details": {
            "binding_part": reverse_primer_data['binding_part'],
            "length": reverse_primer_data['length'],
            "gc_content": reverse_primer_data['gc_content'],
            "tm": reverse_primer_data['tm'],
            "notes": reverse_primer_data['notes']
        },
        "overall_notes": "Primers designed considering length, GC content, and Tm. Tm calculated using Nearest-Neighbor method."
    }
