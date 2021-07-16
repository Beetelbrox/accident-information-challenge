import io
import csv

from typing import List, Optional, Dict

class CSVSanitizer(io.TextIOBase):
    def __init__(self, file, column_name_mapping: Dict[str, str], sep: str=',', replacement_sep: str='|', quote: str='"'):
        self._csv_iter = csv.reader(file, delimiter=sep, quotechar=quote)
        self._buffer = ''
        self._sep = sep
        self._replacement_sep = replacement_sep
        self._quote = quote
        self._is_field_included = self._process_header(column_name_mapping)
    
    def _process_header(self, column_name_mapping: Dict[str, str]) -> str:
        header_tokens = next(self._csv_iter)
        # Initialize the buffer with the sanitized header
        self._buffer += self._build_sanitized_row((column_name_mapping[c] for c in header_tokens if c in column_name_mapping))
        return [col in column_name_mapping for col in header_tokens]
    
    def _sanitize_token(self, token: str) -> str:
        return token.replace(self._quote, '')

    def _filter_columns(self, tokens: List[str]) -> List[str]:
        return (t for i, t in enumerate(tokens) if self._is_field_included[i])
    
    def _build_sanitized_row(self, tokens: List[str]) -> str:
        return self._replacement_sep.join((self._sanitize_token(t) for t in tokens)) + '\n'

    def _read1(self, n: Optional[int] = None) -> str:
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
        return True