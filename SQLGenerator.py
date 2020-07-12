class SQLGenerator:
    def __init__(self,input_name,output_name,output_nick,where=None):
        if where is None:
            where = 'True'
        self.sql_string = 'select * from %s where %s'%(input_name,where)
        self.output_nick = output_nick
        self.output_name = output_name
        self.current_layer = 0

    def select(self,select,where=None):
        if where is None:
            where = 'True'
        self.sql_string = '\n'.join(['\t'+line for line in self.sql_string.split('\n')])
        select_string = '\n,'.join(select)
        layer_name = '%s_%s'%(self.output_nick,self.current_layer)
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
        layer_name = '%s_%s'%(self.output_nick,self.current_layer)
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
        layer_name = '%s_%s'%(self.output_nick,self.current_layer)
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
        layer_name = '%s_%s'%(self.output_nick,self.current_layer)
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
        layer_name = '%s_%s'%(self.output_nick,self.current_layer)
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
        layer_name = '%s_%s'%(self.output_nick,self.current_layer)
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
        self.layer_name_left = '%s_%s'%(self.output_nick,self.current_layer)
        self.layer_name_right = '%s_%s'%(target_table_sql_generator.output_nick,target_table_sql_generator.current_layer)
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
    
    
    def get_sql(self,drop = False):
        self.sql_string = 'create table %s as \n%s' %(self.output_name,self.sql_string)+'\n;'
        if drop:
            self.sql_string = 'drop table if exists %s;\n'%self.output_name+self.sql_string
        print(self.sql_string)

    

table_left = SQLGenerator('the_from_table','table_final','tt','dt=20200101')
table_right = SQLGenerator('the_right_from_table','','bb','dt=20200101')

table_left.select(['name1','a','namea','nameb'])\
.where('a>0')\
.left_join(table_right,on='left.a = right.b')\
.rename('name1','name2')\
.rename_multiple([['namea','namec'],['nameb','named']])\
.UDF('UDFc',['a','b'],'c')\
.UDF_multiple([['UDF1',['a','b'],'c'],['UDF2',['p','q'],'r']])\
.get_sql(drop=True)
