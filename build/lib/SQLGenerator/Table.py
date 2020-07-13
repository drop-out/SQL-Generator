
#coding=utf-8

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
class Table:
    nick_list = ['ADD','ALL','ALTER','AND','AS','ASC','BETWEEN','BIGINT','BOOLEAN','BY','CASE','CAST','COLUMN','COMMENT','CREATE','DESC','DISTINCT','DISTRIBUTE','DOUBLE','DROP','ELSE','FALSE','FROM','FULL','GROUP','IF','IN','INSERT','INTO','IS','JOIN','LEFT','LIFECYCLE','LIKE','LIMIT','MAPJOIN','NOT','NULL','ON','OR','ORDER','OUTER','OVERWRITE','PARTITION','RENAME','REPLACE','RIGHT','RLIKE','SELECT','SORT','STRING','TABLE','THEN','TOUCH','TRUE','UNION','VIEW','WHEN','WHERE']
    suggest_pick = 0
    
    def reset_nick():
        Table.nick_list = ['ADD','ALL','ALTER','AND','AS','ASC','BETWEEN','BIGINT','BOOLEAN','BY','CASE','CAST','COLUMN','COMMENT','CREATE','DESC','DISTINCT','DISTRIBUTE','DOUBLE','DROP','ELSE','FALSE','FROM','FULL','GROUP','IF','IN','INSERT','INTO','IS','JOIN','LEFT','LIFECYCLE','LIKE','LIMIT','MAPJOIN','NOT','NULL','ON','OR','ORDER','OUTER','OVERWRITE','PARTITION','RENAME','REPLACE','RIGHT','RLIKE','SELECT','SORT','STRING','TABLE','THEN','TOUCH','TRUE','UNION','VIEW','WHEN','WHERE']
        Table.suggest_pick = 0
    
    def __init__(self,name,where=None,select=None):
        while True:
            nick = []
            current_pick = Table.suggest_pick
            nick.append(alphabet[current_pick%26])
            current_pick = current_pick//26
            while current_pick>0:
                current_pick = current_pick//26
                nick.append(alphabet[current_pick%26])
            nick = ''.join(nick[::-1])
            if nick not in Table.nick_list:
                Table.nick_list.append(nick)
                self.nick = nick
                break
            else:
                Table.suggest_pick+=1
                
        if select is None:
            select = '*'
        else:
            select = '\n,'.join(select)
        if where is None:
            where = 'True'
        self.sql_string = 'select\n%s\nfrom %s\nwhere %s'%(select,name,where)
        self.current_layer = 0

    def select(self,select,where=None):
        if where is None:
            where = 'True'
        self.sql_string = '\n'.join(['\t'+line for line in self.sql_string.split('\n')])
        select_string = '\n,'.join(select)
        layer_name = '%s_%s'%(self.nick,self.current_layer)
        self.sql_string = '''select 
%s
from
\t(
%s
\t) %s
where %s'''%(select_string,self.sql_string,layer_name,where)
        self.current_layer+=1
        return self
        
    def where(self,where):
        self.sql_string = '\n'.join(['\t'+line for line in self.sql_string.split('\n')])
        layer_name = '%s_%s'%(self.nick,self.current_layer)
        self.sql_string = '''select 
*
from
\t(
%s
\t) %s
where %s'''%(self.sql_string,layer_name,where)
        self.current_layer+=1
        return self
        
    def rename(self,original_name,new_name):
        self.sql_string = '\n'.join(['\t'+line for line in self.sql_string.split('\n')])
        rename_string = '%s as %s'%(original_name,new_name)
        layer_name = '%s_%s'%(self.nick,self.current_layer)
        self.sql_string = '''select 
*
,%s
from
\t(
%s
\t) %s'''%(rename_string,self.sql_string,layer_name)
        self.current_layer+=1
        return self
    
    def rename_multiple(self,rename_struct):
        self.sql_string = '\n'.join(['\t'+line for line in self.sql_string.split('\n')])
        rename_string = '\n,'.join(['%s as %s'%(i[0],i[1]) for i in rename_struct])
        layer_name = '%s_%s'%(self.nick,self.current_layer)
        self.sql_string = '''select 
*
,%s
from
\t(
%s
\t) %s'''%(rename_string,self.sql_string,layer_name)
        self.current_layer+=1
        return self
    
    
    def UDF(self,UDF_name,input_name_list,output_name):
        self.sql_string = '\n'.join(['\t'+line for line in self.sql_string.split('\n')])
        UDF_string = '%s(%s) as %s'%(UDF_name,','.join(input_name_list),output_name)
        layer_name = '%s_%s'%(self.nick,self.current_layer)
        self.sql_string = '''select 
*
,%s
from
\t(
%s
\t) %s'''%(UDF_string,self.sql_string,layer_name)
        self.current_layer+=1
        return self
    
    def UDF_multiple(self,UDF_struct):
        self.sql_string = '\n'.join(['\t'+line for line in self.sql_string.split('\n')])
        UDF_string = '\n,'.join(['%s(%s) as %s'%(i[0],','.join(i[1]),i[2]) for i in UDF_struct])
        layer_name = '%s_%s'%(self.nick,self.current_layer)
        self.sql_string = '''select 
*
,%s
from
\t(
%s
\t) %s'''%(UDF_string,self.sql_string,layer_name)
        self.current_layer+=1
        return self
    
    def join(self,target_table,on,how='left outer'):
        self.sql_left = '\n'.join(['\t'+line for line in self.sql_string.split('\n')])
        self.sql_right = '\n'.join(['\t'+line for line in target_table.sql_string.split('\n')])
        self.layer_name_left = '%s_%s'%(self.nick,self.current_layer)
        self.layer_name_right = '%s_%s'%(target_table.nick,target_table.current_layer)
        self.sql_on_condition = on.replace('left',self.layer_name_left).replace('right',self.layer_name_right)
        self.sql_string = '''select 
*
from
\t(
%s
\t) %s
%s join
\t(
%s
\t) %s
on %s'''%(self.sql_left,self.layer_name_left,how,self.sql_right,self.layer_name_right,self.sql_on_condition)
        self.current_layer+=1
        return self
    
    def left_join(self,target_table,on):
        return self.join(target_table,on,how='left outer')
    
    def right_join(self,target_table,on):
        return self.join(target_table,on,how='right outer')
    
    def inner_join(self,target_table,on):
        return self.join(target_table,on,how='inner')

    def full_join(self,target_table,on):
        return self.join(target_table,on,how='full outer')
    
    
    def create(self,name,drop = False):
        self.sql_string = 'create table %s as \n%s' %(name,self.sql_string)+'\n;'
        if drop:
            self.sql_string = 'drop table if exists %s;\n'%name+self.sql_string
        print(self.sql_string)

