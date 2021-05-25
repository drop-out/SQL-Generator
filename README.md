# SQL-Generator
Generate SQL script with Pandas-like Python code

### Supported features:
1. Automatically generate SQL script for you
2. Automatically formatting
3. Support complicated nested join
4. Name the staging table automatically, such as A_0,A_1,A_2 ...

### Generated script example:
```sql
create table table_final as 
select 
*
,cast(namesum as string) as namesum_string
from
	(
	select 
	*
	,name2+named as namesum
	from
		(
		select 
		*
		from
			(
			select 
			name1
			,name2
			from
				(
				select
				*
				from the_left_table
				where dt=20200101
				) A_0
			where True
			) A_1
		left outer join
			(
			select 
			namec
			,named
			from
				(
				select
				*
				from the_right_table
				where dt=20200101
				) B_0
			where True
			) B_1
		on A_1.name1 = B_1.namec
		) A_2
	) A_3
;
```

Note that the seemingly complicated SQL script is generated with only a few lines of Python code:
```python
table_left = Table('the_left_table','dt=20200101').select(['name1','name2'])
table_right = Table('the_right_table','dt=20200101').select(['namec','named'])

table_left.left_join(table_right,on='left.name1 = right.namec')\
.expression('var1+var2',['name2','named'],'namesum')\
.expression('cast(var1 as string)',['namesum'],'namesum_string')\
.create('table_final')
```

# Install
```bash
pip install https://github.com/drop-out/SQL-Generator/raw/master/dist/SQLGenerator-by-dropout-0.0.4.tar.gz --no-cache
```

# Example
```python
from SQLGenerator import Table
```
### Example1: Select with condition
```python
Table('from_table').select(['a','b','a+b as c']).where('c>0').create('result_table')
```

### Example2: Join two table
```python
table_left = Table('the_left_table','dt=20200101').select(['name1','name2'])
table_right = Table('the_right_table','dt=20200101').select(['namec','named'])

table_left.left_join(table_right,on='left.name1 = right.namec').create('table_final',drop=True)
```
