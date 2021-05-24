
#coding=utf-8

import re

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
    
    
    def function(self,function_name,input_name_list,output_name):
        self.sql_string = '\n'.join(['\t'+line for line in self.sql_string.split('\n')])
        function_string = '%s(%s) as %s'%(function_name,','.join(input_name_list),output_name)
        layer_name = '%s_%s'%(self.nick,self.current_layer)
        self.sql_string = '''select 
*
,%s
from
\t(
%s
\t) %s'''%(function_string,self.sql_string,layer_name)
        self.current_layer+=1
        return self
    
    def function_multiple(self,function_struct):
        '''function_struct格式: [[function_name,[var1,...,varn],output_name]]*n'''
        self.sql_string = '\n'.join(['\t'+line for line in self.sql_string.split('\n')])
        function_string = '\n,'.join(['%s(%s) as %s'%(i[0],','.join(i[1]),i[2]) for i in function_struct])
        layer_name = '%s_%s'%(self.nick,self.current_layer)
        self.sql_string = '''select 
*
,%s
from
\t(
%s
\t) %s'''%(function_string,self.sql_string,layer_name)
        self.current_layer+=1
        return self
    
    def expression(self,expression_string,input_name_list,output_name):
        '''表达式,表达式中的输入变量用var1,var2...表示,如:substr(cast(var1 as string),1,var2)'''
        self.sql_string = '\n'.join(['\t'+line for line in self.sql_string.split('\n')])
        function_string = expression_string
        for i in range(len(input_name_list)):
            function_string = function_string.replace('var%s'%(i+1),input_name_list[i])
        function_string = '%s as %s'%(function_string,output_name)
        layer_name = '%s_%s'%(self.nick,self.current_layer)
        self.sql_string = '''select 
*
,%s
from
\t(
%s
\t) %s'''%(function_string,self.sql_string,layer_name)
        self.current_layer+=1
        return self
    
    def expression_multiple(self,expression_struct):
        '''
        表达式,表达式中的输入变量用var1,var2...表示,如:substr(cast(var1 as string),1,var2)
        function_struct格式: [[function_expression,[var1,...,varn],output_name]]*n
        '''
        self.sql_string = '\n'.join(['\t'+line for line in self.sql_string.split('\n')])
        function_string_list = []
        for expression_struct_i in expression_struct:
            function_string = expression_struct_i[0]
            input_name_list = expression_struct_i[1]
            output_name = expression_struct_i[2]
            for i in range(len(input_name_list)):
                function_string = function_string.replace('var%s'%(i+1),input_name_list[i])
            function_string = '%s as %s'%(function_string,output_name)
            function_string_list.append(function_string)
        function_string = '\n,'.join(function_string_list)
        layer_name = '%s_%s'%(self.nick,self.current_layer)
        self.sql_string = '''select 
*
,%s
from
\t(
%s
\t) %s'''%(function_string,self.sql_string,layer_name)
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
    
    def union(self,target_tables):
        self.sql_string = '\n'.join(['\t'+line for line in self.sql_string.split('\n')])
        sql_to_union = ['\n'.join(['\t'+line for line in target_table.sql_string.split('\n')]) for target_table in target_tables]
        
        for i in sql_to_union:
            self.sql_string = self.sql_string +'\nunion\n' + i + '\n'
            
        return self
    
    def union_all(self,target_tables):
        self.sql_string = '\n'.join(['\t'+line for line in self.sql_string.split('\n')])
        sql_to_union = ['\n'.join(['\t'+line for line in target_table.sql_string.split('\n')]) for target_table in target_tables]
        
        for i in sql_to_union:
            self.sql_string = self.sql_string +'\nunion all\n' + i + '\n'
            
        return self
    
    
    def create(self,name,drop = False):
        self.sql_string = 'create table %s as \n%s' %(name,self.sql_string)+'\n;'
        if drop:
            self.sql_string = 'drop table if exists %s;\n'%name+self.sql_string
        print(self.sql_string)



def tab_remover(line):
    '''用于删除多余的tab
    '''
    if line is None or line=='':
        return line
    line_split = line.split('\n')
    boolean_could_tab_remove = True # 默认可以移除
    boolean_need_tab_remove = False # 默认无需移除
    # 两个boolean标记，是为了避免多行空字符('')串进入死循环
    for l in line_split:
        if l=='':
            pass
        elif l[0]=='\t' or l[:4]=='    ':
            boolean_need_tab_remove = True # 只要有一个'\t'或'    ',就需要移除
        else:
            boolean_could_tab_remove = False # 只要有一行不在('','\t','    ')范围内，就无法移除
    if boolean_need_tab_remove and boolean_could_tab_remove: # 需要且可以移除
        for i in range(len(line_split)):
            if line_split[i]=='':
                pass
            elif line_split[i][0]=='\t':
                line_split[i] = line_split[i][1:]
            else:
                line_split[i] = line_split[i][4:]
        return tab_remover('\n'.join(line_split))
    return line

pattern_comment_line = re.compile(r'\n{0,1}(--|#).*?\n')
def comments_remover(code_string):
    '''
    用于删除注释
    示例数据如下
    code_string="""
    ,aaaa as aaa
    ,bbbb as bbb--注释
    # 注释
    # 注释
    ,cccc as ccc
    """
    用re.sub一次性去掉注释会有问题，注释之间会overlap(多行注释)
    result = re.sub(r'\n{0,1}(--|#).*?\n','\n',s)
    '''
    result = code_string
    
    while re.search(pattern_comment_line,result):
        result = re.sub(pattern_comment_line,'\n',result,1)
    
    return result



def column_parser(code_string):
    '''
    用于提取列名
    parameters:
        code_string: 代码片段
    return: list of name(string)
    '''
    result = comments_remover(code_string) # 移除注释
    result = re.sub(r'[,\s\n\t]cast[\s\n\t]*\(.+[\s\n\t]+as[\s\n\t]+.*?\)','',result) # 移除cast(... as ..) pattern
    result = re.findall(r'[\s\n\t]+as[\s\n\t]+(.*?)[,\s\n\t]',result) # 提取剩余所有的as
    return result