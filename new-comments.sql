with tables as (
-- TABLES
select
	tab.table_id as id,
	'VPDW' table_database,
	tab.table_schema,
	tab.table_name,
	'TABLE' table_type,
	tab.owner_name table_owner,
	col.column_id,
	col.column_name,
	col.ordinal_position column_index,
	col.data_type column_type
from
	v_catalog.tables tab
join
	v_catalog.columns col
	on
	tab.table_id = col.table_id
where
	tab.table_schema = 'MY_SCHEMA'
	and
	lower(tab.table_name) in (
		'stg__a',
		'stg__b',
		'stg__c',
		'seed__a',
		'seed__b',
		'seed__c'
	)
), views as (
-- VIEWS
select
	vw.table_id as id,
	'VPDW' table_database,
	vw.table_schema,
	vw.table_name,
	'VIEW' table_type,
	vw.owner_name table_owner,
	col.column_id,
	col.column_name,
	col.ordinal_position column_index,
	col.data_type column_type
from
	v_catalog.views vw
join
	v_catalog.view_columns col
	on
	vw.table_id = col.table_id
where
	vw.table_schema = 'jzc004'
	and
	lower(vw.table_name) in ('newview')
), table_comments as (
	select
		oid as id,
		objectoid as table_id,
		comment
	from
		v_internal.vs_comments_p com
	where
		objectoid in (select id from tables)
), view_comments as (
	select
		oid as id,
		objectoid as view_id,
		comment
	from
		v_internal.vs_comments_p com
	where
		objectoid in (select id from views)
), tables_with_comments as (
	select
		t.*,
		tc.comment as table_comment
	from
		tables t
	left join table_comments tc on
		t.id = tc.table_id
), views_with_comments as (
	select
		v.*,
		vc.comment as table_comment
	from
		views v
	left join view_comments vc on
		v.id = vc.view_id
), tables_and_views as (
	select
		*
	from
		tables_with_comments twc
	union all
	select
		*
	from
		views_with_comments vwc
)
select
	tav.*,
	com.comment as column_comment
from
	tables_and_views tav
left join
	v_internal.vs_sub_comments com
on
	com.objectoid = split_part(tav.column_id, '-', 1)::int
	and
	com.childobject = tav.column_name
;
