#connect
%load_ext sql
%sql postgres://{username}:{password}@{host}/{db}

#get version
%%sql
SELECT version()