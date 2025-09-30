#!/usr/bin/env python3
"""
Script para crear un archivo sample con las primeras 7 hojas de USERNAME.xlsx
"""

import pandas as pd
import openpyxl
import sys
from pathlib import Path

def create_username_sample(input_file, output_file, max_sheets=7):
    """
    Crear un archivo sample con las primeras N hojas del archivo original.
    
    Args:
        input_file: Ruta al archivo USERNAME.xlsx original
        output_file: Ruta donde guardar el archivo sample
        max_sheets: Número máximo de hojas a incluir (default: 7)
    """
    try:
        # Leer el archivo Excel original
        print(f"Leyendo archivo original: {input_file}")
        workbook = openpyxl.load_workbook(input_file)
        
        # Obtener nombres de todas las hojas
        all_sheets = workbook.sheetnames
        print(f"Total de hojas encontradas: {len(all_sheets)}")
        print(f"Hojas disponibles: {all_sheets}")
        
        # Seleccionar las primeras N hojas
        sheets_to_copy = all_sheets[:max_sheets]
        print(f"Hojas a copiar ({len(sheets_to_copy)}): {sheets_to_copy}")
        
        # Crear nuevo workbook
        new_workbook = openpyxl.Workbook()
        
        # Eliminar la hoja por defecto
        if 'Sheet' in new_workbook.sheetnames:
            new_workbook.remove(new_workbook['Sheet'])
        
        # Copiar cada hoja seleccionada
        for sheet_name in sheets_to_copy:
            print(f"Copiando hoja: {sheet_name}")
            
            # Obtener la hoja original
            original_sheet = workbook[sheet_name]
            
            # Crear nueva hoja
            new_sheet = new_workbook.create_sheet(title=sheet_name)
            
            # Copiar todos los datos y formato
            for row in original_sheet.iter_rows():
                new_row = []
                for cell in row:
                    new_row.append(cell.value)
                new_sheet.append(new_row)
            
            # Copiar ancho de columnas
            for col_letter in original_sheet.column_dimensions:
                new_sheet.column_dimensions[col_letter].width = original_sheet.column_dimensions[col_letter].width
            
            # Copiar altura de filas
            for row_num in original_sheet.row_dimensions:
                new_sheet.row_dimensions[row_num].height = original_sheet.row_dimensions[row_num].height
        
        # Guardar el nuevo archivo
        print(f"Guardando archivo sample: {output_file}")
        new_workbook.save(output_file)
        
        print("✅ Archivo sample creado exitosamente!")
        print(f"Archivo original: {input_file}")
        print(f"Archivo sample: {output_file}")
        print(f"Hojas incluidas: {len(sheets_to_copy)} de {len(all_sheets)}")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {input_file}")
        return False
    except Exception as e:
        print(f"❌ Error procesando el archivo: {e}")
        return False

if __name__ == "__main__":
    # Configurar rutas
    project_root = Path(__file__).parent.parent
    input_file = project_root / "data" / "USERNAME.xlsx"
    output_file = project_root / "data" / "USERNAME_sample_7sheets.xlsx"
    
    # Verificar que el archivo original existe
    if not input_file.exists():
        print(f"❌ Error: El archivo {input_file} no existe")
        sys.exit(1)
    
    # Crear el archivo sample
    success = create_username_sample(str(input_file), str(output_file), max_sheets=7)
    
    if success:
        print(f"\n🎉 Proceso completado!")
        print(f"Archivo sample guardado en: {output_file}")
    else:
        print(f"\n❌ El proceso falló")
        sys.exit(1)