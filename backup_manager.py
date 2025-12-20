import os
import json
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from config import Config

class BackupManager:
    def __init__(self, db_path='qat_app.db'):
        self.db_path = db_path
        self.backup_dir = Config.BACKUP_DIR
        
        # Create backup directory if not exists
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def export_to_excel(self):
        """Export entire database to Excel file"""
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'qat_backup_{timestamp}.xlsx'
        filepath = os.path.join(self.backup_dir, filename)
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        
        # Get all tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for table_name in tables:
                table_name = table_name[0]
                
                # Skip sqlite_sequence table
                if table_name == 'sqlite_sequence':
                    continue
                
                # Read table to DataFrame
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                
                # Write to Excel sheet
                df.to_excel(writer, sheet_name=table_name[:31], index=False)
        
        conn.close()
        
        return filepath
    
    def export_to_json(self):
        """Export entire database to JSON file"""
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'qat_backup_{timestamp}.json'
        filepath = os.path.join(self.backup_dir, filename)
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        data = {
            'export_date': datetime.now().isoformat(),
            'tables': {}
        }
        
        for table_name in tables:
            table_name = table_name[0]
            
            # Skip sqlite_sequence table
            if table_name == 'sqlite_sequence':
                continue
            
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            data['tables'][table_name] = [dict(row) for row in rows]
        
        # Write to JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        conn.close()
        
        return filepath
    
    def list_backups(self):
        """List all backup files"""
        
        backups = []
        
        for filename in os.listdir(self.backup_dir):
            filepath = os.path.join(self.backup_dir, filename)
            
            if os.path.isfile(filepath) and filename.startswith('qat_backup_'):
                stat = os.stat(filepath)
                
                backups.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_ctime),
                    'extension': os.path.splitext(filename)[1]
                })
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return backups
    
    def cleanup_old_backups(self):
        """Delete backups older than retention period"""
        
        cutoff_date = datetime.now() - timedelta(days=Config.BACKUP_RETENTION_DAYS)
        deleted_count = 0
        
        for backup in self.list_backups():
            if backup['created_at'] < cutoff_date:
                try:
                    os.remove(backup['filepath'])
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {backup['filename']}: {e}")
        
        return deleted_count
    
    def restore_from_backup(self, backup_path):
        """Restore database from backup file"""
        
        # Create backup of current database
        self.export_to_excel()
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data (keep structure)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table_name in tables:
            table_name = table_name[0]
            if table_name != 'sqlite_sequence':
                cursor.execute(f"DELETE FROM {table_name}")
        
        conn.commit()
        
        # Restore from backup based on file type
        if backup_path.endswith('.json'):
            self._restore_from_json(backup_path, conn)
        elif backup_path.endswith('.xlsx'):
            self._restore_from_excel(backup_path, conn)
        else:
            raise ValueError("Unsupported backup file format")
        
        conn.close()
    
    def _restore_from_json(self, json_path, conn):
        """Restore from JSON backup"""
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cursor = conn.cursor()
        
        for table_name, rows in data['tables'].items():
            if not rows:
                continue
            
            # Get column names
            columns = rows[0].keys()
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['?' for _ in columns])
            
            for row in rows:
                values = [row[col] for col in columns]
                cursor.execute(
                    f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})",
                    values
                )
        
        conn.commit()
    
    def _restore_from_excel(self, excel_path, conn):
        """Restore from Excel backup"""
        
        xls = pd.ExcelFile(excel_path)
        cursor = conn.cursor()
        
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            if df.empty:
                continue
            
            # Convert NaN to None
            df = df.where(pd.notnull(df), None)
            
            # Insert data
            for _, row in df.iterrows():
                columns = row.index.tolist()
                values = row.tolist()
                
                columns_str = ', '.join(columns)
                placeholders = ', '.join(['?' for _ in columns])
                
                cursor.execute(
                    f"INSERT INTO {sheet_name} ({columns_str}) VALUES ({placeholders})",
                    values
                )
        
        conn.commit()

# Singleton instance
backup_manager = BackupManager()
