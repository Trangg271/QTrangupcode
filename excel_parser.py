import os
import openpyxl
from datetime import datetime

def load_workbook_unmerged(xlsx_path):
    """
    Loads an Excel file and unmerges all cells by propagating the top-left value
    across the entire merged rectangle.
    Returns a dict mapping sheet_name -> 2D list of cell values.
    """
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    sheets_data = {}
    
    for sname in wb.sheetnames:
        ws = wb[sname]
        # Build 2D grid
        grid = [[ws.cell(r, c).value for c in range(1, ws.max_column + 1)] for r in range(1, ws.max_row + 1)]
        
        # Propagate merged cell values
        for mrange in list(ws.merged_cells.ranges):
            min_col, min_row, max_col, max_row = mrange.min_col, mrange.min_row, mrange.max_col, mrange.max_row
            top_left_val = ws.cell(min_row, min_col).value
            for r in range(min_row, max_row + 1):
                for c in range(min_col, max_col + 1):
                    grid[r - 1][c - 1] = top_left_val
        
        # Remove trailing completely empty rows
        while grid and not any(cell is not None and str(cell).strip() != '' for cell in grid[-1]):
            grid.pop()
            
        if not grid:
            continue
            
        # Remove trailing completely empty columns
        max_valid_col = 0
        for row in grid:
            for c_idx in range(len(row) - 1, -1, -1):
                if row[c_idx] is not None and str(row[c_idx]).strip() != '':
                    max_valid_col = max(max_valid_col, c_idx + 1)
                    break
        
        grid = [row[:max_valid_col] for row in grid]
        sheets_data[sname] = grid
        
    return sheets_data

def format_cell_value(val):
    if val is None:
        return ""
    if isinstance(val, datetime):
        return val.strftime('%Y-%m-%d')
    if isinstance(val, float):
        # If float is integer, show as integer or clean float
        if val.is_integer():
            return str(int(val))
        return f"{val:.4f}".rstrip('0').rstrip('.')
    return str(val).replace('\n', ' ').strip()

def grid_to_markdown(grid, max_rows=150):
    """
    Converts an unmerged 2D grid into a clean Markdown table representation
    with row numbers for easy spatial reference by the LLM.
    """
    if not grid:
        return ""
    
    lines = []
    for r_idx, row in enumerate(grid[:max_rows], 1):
        formatted_cells = [format_cell_value(c) for c in row]
        row_str = " | ".join(formatted_cells)
        lines.append(f"Row {r_idx:02d}: | {row_str} |")
        
    if len(grid) > max_rows:
        lines.append(f"... (total {len(grid)} rows, showing first {max_rows})")
        
    return "\n".join(lines)

def get_excel_context(xlsx_path):
    """
    Returns full textual context of all sheets in the Excel file.
    """
    sheets_data = load_workbook_unmerged(xlsx_path)
    context_parts = []
    
    for sname, grid in sheets_data.items():
        md = grid_to_markdown(grid)
        context_parts.append(f"### Sheet: '{sname}' ({len(grid)} rows x {len(grid[0]) if grid else 0} cols):\n{md}")
        
    return "\n\n".join(context_parts)
