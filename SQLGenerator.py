alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
class SQLGenerator:
    nick_list = ['ADD','ALL','ALTER','AND','AS','ASC','BETWEEN','BIGINT','BOOLEAN','BY','CASE','CAST','COLUMN','COMMENT','CREATE','DESC','DISTINCT','DISTRIBUTE','DOUBLE','DROP','ELSE','FALSE','FROM','FULL','GROUP','IF','IN','INSERT','INTO','IS','JOIN','LEFT','LIFECYCLE','LIKE','LIMIT','MAPJOIN','NOT','NULL','ON','OR','ORDER','OUTER','OVERWRITE','PARTITION','RENAME','REPLACE','RIGHT','RLIKE','SELECT','SORT','STRING','TABLE','THEN','TOUCH','TRUE','UNION','VIEW','WHEN','WHERE']
    suggest_pick = 0
    
    def reset_nick():
        SQLGenerator.nick_list = ['ADD','ALL','ALTER','AND','AS','ASC','BETWEEN','BIGINT','BOOLEAN','BY','CASE','CAST','COLUMN','COMMENT','CREATE','DESC','DISTINCT','DISTRIBUTE','DOUBLE','DROP','ELSE','FALSE','FROM','FULL','GROUP','IF','IN','INSERT','INTO','IS','JOIN','LEFT','LIFECYCLE','LIKE','LIMIT','MAPJOIN','NOT','NULL','ON','OR','ORDER','OUTER','OVERWRITE','PARTITION','RENAME','REPLACE','RIGHT','RLIKE','SELECT','SORT','STRING','TABLE','THEN','TOUCH','TRUE','UNION','VIEW','WHEN','WHERE']
        SQLGenerator.suggest_pick = 0
    
    def __init__(self,input_table,where=None,select=None):
        while True:
            nick = []
            current_pick = SQLGenerator.suggest_pick
            nick.append(alphabet[current_pick%26])
            current_pick = current_pick//26
            while current_pick>0:
                current_pick = current_pick//26
                nick.append(alphabet[current_pick%26])
            nick = ''.join(nick[::-1])
            if nick not in SQLGenerator.nick_list:
                SQLGenerator.nick_list.append(nick)
                self.nick = nick
                break
            else:
                SQLGenerator.suggest_pick+=1
                
        if select is None:
            select = '*'
        else:
            select = '\n,'.join(select)
        if where is None:
            where = 'True'
        self.sql_string = 'select\n%s\nfrom %s\nwhere %s'%(select,input_table,where)
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
    
    def join(self,target_table_sql_generator,on,how='left outer'):
        self.sql_left = '\n'.join(['\t'+line for line in self.sql_string.split('\n')])
        self.sql_right = '\n'.join(['\t'+line for line in target_table_sql_generator.sql_string.split('\n')])
        self.layer_name_left = '%s_%s'%(self.nick,self.current_layer)
        self.layer_name_right = '%s_%s'%(target_table_sql_generator.nick,target_table_sql_generator.current_layer)
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
    
    def left_join(self,target_table_sql_generator,on):
        return self.join(target_table_sql_generator,on,how='left outer')
    
    def right_join(self,target_table_sql_generator,on):
        return self.join(target_table_sql_generator,on,how='right outer')
    
    def inner_join(self,target_table_sql_generator,on):
        return self.join(target_table_sql_generator,on,how='inner')

    def full_join(self,target_table_sql_generator,on):
        return self.join(target_table_sql_generator,on,how='full outer')
    
    
    def create_table(self,table_name,drop = False):
        self.sql_string = 'create table %s as \n%s' %(table_name,self.sql_string)+'\n;'
        if drop:
            self.sql_string = 'drop table if exists %s;\n'%table_name+self.sql_string
        print(self.sql_string)

    

table_left = SQLGenerator('the_from_table','dt=20200101')
table_right = SQLGenerator('the_right_from_table','dt=20200101')

table_left.select(['name1','a','namea','nameb'])\
.where('a>0')\
.left_join(table_right,on='left.a = right.b')\
.rename('name1','name2')\
.rename_multiple([['namea','namec'],['nameb','named']])\
.UDF('UDFc',['a','b'],'c')\
.UDF_multiple([['UDF1',['a','b'],'c'],['UDF2',['p','q'],'r']])\
.create_table('table_final',drop=True)
