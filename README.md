# Fresnel

[Augustin-Jean Fresnel][wikipedia] was a French engineer who contributed
significantly to the establishment of the theory of wave optics.

Fresnel is a web-based reporting framework for Absolute Manage.

## Prerequisites

To use Fresnel you need an existing Absolute Manage server with ODBC export
properly configured to push data to a MySQL database.

### Views

Some default reports depend on custom views added to the database. Here are the
necessary view definitions.

```sql
create view v_agent_site_codes as
    select agent_info_record_id, value as agent_site_code
    from agent_custom_fields acf
    join custom_field_names cfn on cfn.id = acf.fieldid
    where name = 'site code'
```

```sql
create view v_agent_os_version_strings as
    select agent_info_record_id, concat_ws('.', left(conv(osversion, 10,
    16), length(conv(osversion, 10, 16)) - 2), conv(mid(conv(osversion,
    10, 16), length(conv(osversion, 10, 16)) - 1, 1), 16, 10),
    if(right(conv(osversion, 10, 16), 1) = '0', null,
    right(conv(osversion, 10, 16), 1))) as agent_os_version_string from
    software_info
```

-----

The favicon is from the [Silk icon set][silk].

[wikipedia]: http://en.wikipedia.org/wiki/Augustin-Jean_Fresnel
[silk]: http://www.famfamfam.com/lab/icons/silk/
