require(["nbextensions/snippets_menu/main"], function (snippets_menu) {
    console.log('Loading `snippets_menu` customizations from `custom.js`');
    var horizontal_line = '---';
    var my_favorites = {
        "name" : "Greenplum Database",
        "sub-menu" : [
            {
                "name" : "Connect to Greenplum Database (manual)",
                "snippet" : ["%load_ext sql", 
                    "%sql postgres://{username}:{password}@{host}/{db}"]
            },
            {
                "name" : "Connect to Greenplum Database via pyodbc",
                "snippet" : ["import pyodbc",
                "import pandas\n",                
                "def as_pandas_DataFrame(cursor):",
                "\tnames = [metadata[0] for metadata in cursor.description]",
                "\treturn pandas.DataFrame([dict(zip(names, row)) for row in cursor], columns=names)\n",
                "# Create connection",
                "conn = pyodbc.connect('Driver={PostgeSQL};'",
                                      "f'Server={host};'",
                                      "f'Database={db};'",
                                      "f'UID={username};'",
                                      "f'PWD={password}', autocommit=True)\n",
                "# Get cursor to interact with the SQL engine",
                "cursor = conn.cursor()\n",
                "# Execute queries like so:",
                "cursor.execute('SELECT version()')\n",
                "# Convert result set into pandas DataFrame",
                "df = as_pandas_DataFrame(cursor)\n",
                "# Remember to always close your connection once done, otherwise unexpected behavior may result!",
                "conn.close()"]
            },
            "---",
            {
                "name" : "Get Greenplum Database Version",
                "snippet" : ["%%sql\nSELECT version()"]
            }
        ]
    };
    snippets_menu.options['menus'] = snippets_menu.default_menus;
    snippets_menu.options['menus'][0]['sub-menu'].push(horizontal_line);
    snippets_menu.options['menus'][0]['sub-menu'].push(my_favorites);
    console.log('Loaded `snippets_menu` customizations from `custom.js`');
});