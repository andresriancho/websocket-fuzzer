import logging

INTERESTING_THINGS = ('error',
                      'exception',
                      'sql',
                      'xml',
                      'ldap',
                      'root:x:',
                      'root:!:',
                      'daemon:',
                      'bytes from 127.0.0.1',
                      'trace',
                      'groups=',
                      '%p.%p.%p',
                      'drwxrwxr',
                      'backtrace',
                      'memory map',

                      # Not sure which lang or LDAP engine
                      'supplied argument is not a valid ldap',

                      # Java
                      'javax.naming.NameNotFoundException',
                      'LDAPException',
                      'com.sun.jndi.ldap',

                      # PHP
                      'Bad search filter',

                      # http://support.microsoft.com/kb/218185
                      'Protocol error occurred',
                      'Size limit has exceeded',
                      'An inappropriate matching occurred',
                      'A constraint violation occurred',
                      'The syntax is invalid',
                      'Object does not exist',
                      'The alias is invalid',
                      'The distinguished name has an invalid syntax',
                      'The server does not handle directory requests',
                      'There was a naming violation',
                      'There was an object class violation',
                      'Results returned are too large',
                      'Unknown error occurred',
                      'Local error occurred',
                      'The search filter is incorrect',
                      'The search filter is invalid',
                      'The search filter cannot be recognized',

                      # OpenLDAP
                      'Invalid DN syntax',
                      'No Such Object',

                      # IPWorks LDAP
                      # http://www.tisc-insight.com/newsletters/58.html
                      'IPWorksASP.LDAP',

                      # https://entrack.enfoldsystems.com/browse/SERVERPUB-350
                      'Module Products.LDAPMultiPlugins',

                      'java.io.FileNotFoundException:',
                      'java.lang.Exception:',
                      'java.lang.IllegalArgumentException:',
                      'java.net.MalformedURLException:',

                      # PHP
                      'fread\\(\\):',
                      'for inclusion \'\\(include_path=',
                      'Failed opening required',
                      '<b>Warning</b>:  file\\(',
                      '<b>Warning</b>:  file_get_contents\\(',
                      'open_basedir restriction in effect',

                      # ASP / MSSQL
                      'System.Data.OleDb.OleDbException',
                      '[SQL Server]',
                      '[Microsoft][ODBC SQL Server Driver]',
                      '[SQLServer JDBC Driver]',
                      '[SqlException',
                      'System.Data.SqlClient.SqlException',
                      'Unclosed quotation mark after the character string',
                      "'80040e14'",
                      'mssql_query()',
                      'odbc_exec()',
                      'Microsoft OLE DB Provider for ODBC Drivers',
                      'Microsoft OLE DB Provider for SQL Server',
                      'Incorrect syntax near',
                      'Sintaxis incorrecta cerca de',
                      'Syntax error in string in query expression',
                      'ADODB.Field (0x800A0BCD)<br>',
                      "ADODB.Recordset'",
                      "Unclosed quotation mark before the character string",
                      "'80040e07'",
                      'Microsoft SQL Native Client error',
                      'SQL Server Native Client',
                      'Invalid SQL statement',

                      # DB2
                      'SQLCODE',
                      'DB2 SQL error:',
                      'SQLSTATE',
                      '[CLI Driver]',
                      '[DB2/6000]',

                      # Sybase
                      "Sybase message:",
                      "Sybase Driver",
                      "[SYBASE]",

                      # Access
                      'Syntax error in query expression',
                      'Data type mismatch in criteria expression.',
                      'Microsoft JET Database Engine',
                      '[Microsoft][ODBC Microsoft Access Driver]',

                      # ORACLE
                      'Microsoft OLE DB Provider for Oracle',
                      'wrong number or types',

                      # POSTGRE
                      'PostgreSQL query failed:',
                      'supplied argument is not a valid PostgreSQL result',
                      'unterminated quoted string at or near',
                      'pg_query() [:',
                      'pg_exec() [:',

                      # MYSQL
                      'supplied argument is not a valid MySQL',
                      'Column count doesn\'t match value count at row',
                      'mysql_fetch_array()',
                      'mysql_',
                      'on MySQL result index',
                      'You have an error in your SQL syntax;',
                      'You have an error in your SQL syntax near',
                      'MySQL server version for the right syntax to use',
                      'Division by zero in',
                      'not a valid MySQL result',
                      '[MySQL][ODBC',
                      "Column count doesn't match",
                      "the used select statements have different number of columns",
                      "DBD::mysql::st execute failed",
                      "DBD::mysql::db do failed:",

                      # Informix
                      'com.informix.jdbc',
                      'Dynamic Page Generation Error:',
                      'An illegal character has been found in the statement',
                      '[Informix]',
                      '<b>Warning</b>:  ibase_',
                      'Dynamic SQL Error',

                      # DML
                      '[DM_QUERY_E_SYNTAX]',
                      'has occurred in the vicinity of:',
                      'A Parser Error (syntax error)',

                      # Java
                      'java.sql.SQLException',
                      'Unexpected end of command in statement',

                      # Coldfusion
                      '[Macromedia][SQLServer JDBC Driver]',

                      # SQLite
                      'could not prepare statement',

                      # Generic errors..
                      'Unknown column',
                      'where clause',
                      'SqlServer',
                      'syntax error',
                      'Microsoft OLE DB Provider',

                      # Certs!
                      '-----BEGIN CERTIFICATE-----',
                      '-----BEGIN RSA PRIVATE KEY-----'
                      )


def reverse_len(a, b):
    return cmp(len(b), len(a))


INTERESTING_THINGS = [it.lower() for it in INTERESTING_THINGS]
INTERESTING_THINGS.sort(reverse_len)
INTERESTING_THINGS = set(INTERESTING_THINGS)


def analyze_response(message, ignore_errors):
    """
    Receives a message and tries to identify interesting things in them.

    :param message: The message received by the websocket server
    :return: None, we just print interesting things to output using logging
    """
    message = message.lower()

    for ignore in ignore_errors:
        if ignore in message:
            return False

    for it in INTERESTING_THINGS:
        if it in message:
            return True

    return False
