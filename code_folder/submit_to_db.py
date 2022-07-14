import os
import mysql.connector
#needs mysql_connector_python-8.0.29 installed
#https://dev.mysql.com/downloads/connector/python/


config = {
  'user': 'username',
  'password': 'password',
  'host': 'localhost',
  'database': 'yourdatabase'
}




#access database generate a list of existing filename enteries 
def iterate_db(field_name, table_name):
    """
    expects:
        string of target field name
        string of target table name
    returns:
        strings list containing filenames with expected parameters
    """
    
    cn = mysql.connector.connect(**config)
    cursor = cn.cursor()

    try:
        cursor.execute(f'SELECT {field_name} FROM {table_name}')
        result = cursor.fetchall()
    except mysql.connector.Error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
    
    db_entries = []
     
    for x in result:
        db_entries.append(x[0])
        
    cursor.close()
    cn.close()
    
    return db_entries
    

#access target folder generate a list of existing filename that meet parameters. 
def iterate_directory(path):
    """
    expects:
        raw string of target directory path.
    returns:
        strings list containing filenames that exist in the database.
    """
    
    #change to target directory
    os.chdir(path)
    
    exts = (".png", ".jpeg", ".jpg")
    dir_entries = []
    for images in os.listdir():
        if (images.endswith(exts)):
            dir_entries.append(images)
    return dir_entries

#compare string list of filenames from folder to string list of filenames from database
def compare_db_to_folder(db_enteries, folder_enteries):
    """ 
    expects:
        string list of filenames from database
        string list of filenames from folder
    returns:
        string list of filenames from folder that dont exist in database.
    """
    
    db = set(db_enteries) 
    folder = set(folder_enteries)
    difference = [item for item in folder if item not in db]

    return difference

#helpert function convert list of strings to list of tuple strings
def submit_helper(to_tuple):
    """
        expects:
            string list of filenames.
        returns:
            list of tuple strings of filenames.
    """
    list_tuple = [x for x in zip(*[iter(to_tuple)])]
    return list_tuple

#submit list of new image filenames to the database.
def submit_new_to_db(difference, field_name, table_name):
    """
        expects:
            string list of filenames that dont exist in database
            string of target field name
            string of target table name
        return: 
            none
    """
    
    difference_tuple = submit_helper(difference);
    
    cn = mysql.connector.connect(**config)
    cursor = cn.cursor()
    
    stmt = f"INSERT INTO {table_name} ({field_name}) VALUES (%s)"
    try:
        cursor.executemany(stmt, difference_tuple)
        cn.commit()
    except mysql.connector.Error as err:
        print(err)
        print("Error Code:", err.errno)
        print("SQLSTATE", err.sqlstate)
        print("Message", err.msg)
        cn.rollback()
    
    cursor.close()
    cn.close()
    
def main():
    #Target Folder Path
    #r"" creates a raw string
    path = r"Target foldler path"
    
    #Target field that holds file names
    field_name = 'target field name'
    
    #Target table name in database.
    table_name = 'target table name'
    
    list_db_enteries = iterate_db(field_name, table_name)
    # print(f"database: {list_db_enteries}")
    
    list_folder_enteries = iterate_directory(path)
    # print(f"folder: {list_folder_enteries}")
    
    difference = compare_db_to_folder(list_db_enteries, list_folder_enteries)
    
    #to avoid unecessary access to database if list length is 0 just pass
    if (len(difference) > 0 ):
        # print(f"difference: {difference}")
        submit_new_to_db(difference, field_name, table_name)
    
if __name__ == "__main__":
    main()