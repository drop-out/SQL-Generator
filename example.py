from SQLGenerator import Table

table_left = Table('the_from_table','dt=20200101')
table_right = Table('the_right_from_table','dt=20200101')

table_left.select(['name1','namea','nameb'])\
.where('condition_a>0')\
.left_join(table_right,on='left.a = right.b')\
.rename('name1','name2')\
.rename_multiple([['namea','namec'],['nameb','named']])\
.function('',['a','b'],'c')\
.complicated_function_multiple([['cast(var1 as string)',['d'],'e'],['(var1+var2)',['p','q'],'r']])\
.create('table_final',drop=True)
