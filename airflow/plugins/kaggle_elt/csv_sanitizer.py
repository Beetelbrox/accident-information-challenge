import io
import csv

from typing import List, Optional, Dict

class CSVSanitizer(io.TextIOBase):
    """
    A class that read and sanitize a csv file in an streaming fashion. Implements a
    file-like interface so it can be consumed without having to read the whole thing
    into memory.
    """
    def __init__(self, file, column_name_mapping: Dict[str, str], sep: str=',', replacement_sep: str='|', quote: str='"'):
        """Constructs all necessary attributes for the object"""
        self._csv_iter = csv.reader(file, delimiter=sep, quotechar=quote)
        self._buffer = ''
        self._sep = sep
        self._replacement_sep = replacement_sep
        self._quote = quote
        # Mask for the included fields
        self._is_field_included = self._process_header(column_name_mapping)
    
    def _process_header(self, column_name_mapping: Dict[str, str]) -> str:
        """Reads the csv header, sanitizes it and returns the mask of included fields"""
        header_tokens = next(self._csv_iter)
        # Initialize the buffer with the sanitized header
        self._buffer += self._build_sanitized_row((column_name_mapping[c] for c in header_tokens if c in column_name_mapping))
        return [col in column_name_mapping for col in header_tokens]
    
    def _sanitize_token(self, token: str) -> str:
        """Removes quotes from a given token"""
        return token.replace(self._quote, '')

    def _filter_columns(self, tokens: List[str]) -> List[str]:
        """Removes all tokens whose column is not included in the output file"""
        return (t for i, t in enumerate(tokens) if self._is_field_included[i])
    
    def _build_sanitized_row(self, tokens: List[str]) -> str:
        """Concatenates sanitized tokens into a sanitized row"""
        return self._replacement_sep.join((self._sanitize_token(t) for t in tokens)) + '\n'

    def _read1(self, n: Optional[int] = None) -> str:
        """Reads a new line or tries to read from buffer"""
        if not self._buffer:
            try:
                filtered_tokens = self._filter_columns(next(self._csv_iter))
                self._buffer = self._build_sanitized_row(filtered_tokens)
            except StopIteration:
                pass
        ret = self._buffer[:n]
        self._buffer = self._buffer[len(ret):]
        return ret

    def read(self, n: Optional[int] = None) -> str:
        """Reads n characters from the input"""
        line = []
        if n is None or n < 0:
            while True:
                m = self._read1()
                if not m: break
                line.append(m)
        else:
            while n > 0:
                m = self._read1(n)
                if not m: break
                n -= len(m)
                line.append(m)
        return ''.join(line)
    
    def readable(self) -> bool:
        """Return true to indicate that the object is readable"""
        return True