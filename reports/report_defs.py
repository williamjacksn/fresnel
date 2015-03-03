class Report(object):
    def __init__(self, report_id, name, description, columns, sql, link=None,
                 prompts=None):
        self.report_id = report_id
        self.name = name
        self.description = description
        self.columns = columns
        self.sql = sql
        self.link = link
        self.prompts = prompts

reports = list()


def report_exists(report_id):
    for report in reports:
        if report.report_id == report_id:
            return True
    return False


def get_report(report_id):
    for report in reports:
        if report.report_id == report_id:
            return report
    raise IndexError("Invalid Report ID: {0}".format(report_id))

adobe_reader_x_latest = "10.1.13"
adobe_reader_xi_latest = "11.0.10"
adobe_reader_xi_latest_mac = "11.0.10"
firefox_latest = "36.0"
flash_player_activex_latest = "16.0.0.305"
flash_player_plugin_latest = "16.0.0.305"
java_latest = "7.0.750"

portable_rlike = "book|latitude|3249|portege"


reports = [

Report(
    report_id=0,
    name="Inv 4: All computers",
    description="All managed computers with site, name, platform, and IPv4 address",
    columns=["Site", "Computer Name", "Platform", "IPv4 Address"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, agentname, enum_value, inet_ntoa(agentipv4) from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join enum_AgentPlatform eap on eap.enum_key = ai.agentplatform order by agentname"
),

Report(
    report_id=1,
    name="Crit 6: Computers with missing critical updates",
    description="All computers that are missing at least one critical operating system update",
    columns=["Computer Name", "Platform", "Missing Updates", "Last Heartbeat"],
    sql="select distinct agentname, enum_value, count(name), date_format(convert_tz(lastheartbeat, '+00:00', 'system'), '%Y-%m-%d %H:%i:%s') as lastheartbeat from agent_info ai join enum_AgentPlatform eap on eap.enum_key = ai.agentplatform join missing_patches_info mpi on mpi.agent_info_record_id = ai.id where name not rlike '^[abdefghiklnpqrxz]|^c[ahlrz]|^jap|mini|supp|^macb|^mig|^sam|^serb|^serve|^s[lnpuw]|^th[au]|^tu|^uk|^windows [ils]' group by agentname, enum_value order by agentname",
    link={
        "target_report_id": 2,
        "target_prompt_name": "agentname"
    }
),

Report(
    report_id=2,
    name="Crit 3: Missing critical OS updates for a computer",
    description="All critical operating system updates that a particular computer is missing",
    columns=["Missing Update Name"],
    sql="select name from agent_info ai join missing_patches_info mpi on mpi.agent_info_record_id = ai.id where name not rlike '^[abdefghiklnpqrxz]|^c[ahlrz]|^jap|mini|supp|^macb|^mig|^sam|^serb|^serve|^s[lnpuw]|^th[au]|^tu|^uk|^windows [ils]' and agentname = %s order by name",
    prompts=["agentname"]
),

Report(
    report_id=3,
    name="Inv 1: Inventory overview",
    description="All sites with a count of total computers in each department",
    columns=["Site", "Total Computers", "Total Mac", "Total Windows"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, count(id) as total_computers, sum(agentplatform = 1) as total_mac, sum(agentplatform = 2) as total_windows from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id group by agent_site_code_n order by agent_site_code_n",
    link={
        "target_report_id": 4,
        "target_prompt_name": "sitecode"
    }
),

Report(
    report_id=4,
    name="Inv 2: Inventory for a site",
    description="Inventory of all computers assigned to a site",
    columns=["Computer Name", "OS", "OS Version", "Current User", "IPv4 Address", "MAC Address", "Memory", "Serial Number", "Manufacturer", "Model", "Warranty End Date", "Warranty Status", "Update OS", "Update Java", "Last Heartbeat"],
    sql="select agentname, eosp.enum_value as os_platform, agent_os_version_string, currentuser, inet_ntoa(agentipv4) as ipv4, primarymacaddress, concat(round(physicalmemorysize / (1073741824), 1), ' GB') as memory, coalesce(machineserialno, systemenclosureserialnumber) as serial_number, case when instr(computermanufacturer, 'apple') > 0 then 'Apple' when instr(computermanufacturer, 'dell') > 0 then 'Dell' when instr(computermanufacturer, 'hewlett') > 0 then 'HP' when instr(computermanufacturer, 'lenovo') > 0 then 'Lenovo' when instr(computermanufacturer, 'microsoft') > 0 then 'Microsoft' when instr(computermanufacturer, 'innotek') > 0 then 'Oracle' when instr(computermanufacturer, 'vmware') > 0 then 'VMware' else computermanufacturer end as computer_manufacturer, coalesce(emm.enum_value, computermodel) as computer_model, date_format(applewarrantyend, '%%Y-%%m-%%d'), applewarrantystatus, if(checkapplesoftwarepatches = 1, 'Yes', 'No') as update_os, if(update_java = 1, 'Yes', 'No') as update_java, date_format(convert_tz(lastheartbeat, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s') as lastheartbeat from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join (select agent_info_record_id, numbervalue as update_java from agent_custom_fields acf left join custom_field_names cfn on cfn.id = acf.fieldid where name='update java') auj on auj.agent_info_record_id = ai.id join hardware_info hi on hi.agent_info_record_id = ai.id join software_info si on si.agent_info_record_id = ai.id left join enum_OSPlatform eosp on eosp.enum_key = si.osplatform left join enum_MachineModel emm on emm.enum_key = hi.computermodel left join v_agent_os_version_strings vs on vs.agent_info_record_id = ai.id where coalesce(agent_site_code, ' NONE') = %s order by agentname",
    prompts=["sitecode"]
),

Report(
    report_id=5,
    name="01 - Crit 1: Critical update compliance overview",
    description="All sites with total computer count and compliant computer count",
    columns=["Site", "Total Computers", "Compliant Computers", "Compliance Percentage"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, count(ai.id) as total_computers, sum(imcp is null) as compliant_computers, round((sum(imcp is null) / count(ai.id)) * 100, 2) as compliance_percentage from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join (select distinct agent_info_record_id, true as imcp from missing_patches_info where name not rlike '^[abdefghiklnpqrxz]|^c[ahlrz]|^jap|mini|supp|^macb|^mig|^sam|^serb|^serve|^s[lnpuw]|^th[au]|^tu|^uk|^windows [ils]') mcp on mcp.agent_info_record_id = ai.id group by agent_site_code_n",
    link={
        "target_report_id": 7,
        "target_prompt_name": "sitecode"
    }
),

Report(
    report_id=6,
    name="03 - AV 1: Antivirus software compliance overview",
    description="All sites with total computer count and compliant computer count; a computer is compliant if it has antivirus software installed",
    columns=["Site", "Total Computers", "Compliant Computers", "Compliance Percentage"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, count(id) as total_computers, coalesce(sum(avi = 1), 0) as total_compliant, round((coalesce(sum(avi = 1), 0) / count(id)) * 100, 2) as compliance_percentage from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join (select distinct agent_info_record_id, true as avi from installed_software_info isi join installed_software_titles ist on ist.id = isi.installed_software_titles_record_id where name in ('clamxav.app', 'fireamp connector', 'microsoft forefront client security antimalware service', 'microsoft forefront endpoint protection', 'microsoft forefront endpoint protection 2010 server management', 'sophos anti-virus.app', 'symantec antivirus', 'symantec antivirus.app', 'system center 2012 endpoint protection.app', 'virusbarrier x6.app')) iav on iav.agent_info_record_id = ai.id group by agent_site_code_n order by agent_site_code_n",
    link={
        "target_report_id": 8,
        "target_prompt_name": "sitecode"
    }
),

Report(
    report_id=7,
    name="Crit 2: Critical update compliance for a site",
    description="All computers in a particular site that are missing critical operating system updates",
    columns=["Computer Name", "Platform", "Number of Missing Updates", "OS Updates Enabled", "Last Missing Updates Scan"],
    sql="select agentname, enum_value as agentplatform, count(mpi.patchidentifier) as number_missing_updates, if(checkapplesoftwarepatches = 1, 'Yes', 'No') as os_updates_enabled, date_format(convert_tz(lastmissingpatchesinfo, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s') as lastmpi from agent_info ai join enum_AgentPlatform eap on eap.enum_key = ai.agentplatform join asset_modification_info ami on ami.agent_info_record_id = ai.id join missing_patches_info mpi on mpi.agent_info_record_id = ai.id left join (select agent_info_record_id, value as sitecode from agent_custom_fields acf left join custom_field_names cfn on cfn.id = acf.fieldid where name='site code') ascd on ascd.agent_info_record_id = ai.id where coalesce(sitecode, ' NONE') = %s and mpi.name not rlike '^[abdefghiklnpqrxz]|^c[ahlrz]|^jap|mini|supp|^macb|^mig|^sam|^serb|^serve|^s[lnpuw]|^th[au]|^tu|^uk|^windows [ils]' group by ai.id order by agentname",
    prompts=["sitecode"],
    link={
        "target_report_id": 2,
        "target_prompt_name": "agentname"
    }
),

Report(
    report_id=8,
    name="AV 2: Antivirus software information for a site",
    description="All computers in a site with the name of antivirus software installed",
    columns=["Computer Name", "Installed Antivirus Software", "Last Software Scan"],
    sql="select agentname, avn, date_format(convert_tz(lastinstalledsoftwareinfo, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s') as lastinstalledsoftwareinfo from agent_info ai left join asset_modification_info ami on ami.agent_info_record_id = ai.id left join (select agent_info_record_id, group_concat(name order by name separator ', ') as avn from installed_software_info isi join installed_software_titles ist on ist.id = isi.installed_software_titles_record_id where name in ('clamxav.app', 'fireamp connector', 'microsoft forefront client security antimalware service', 'microsoft forefront endpoint protection', 'microsoft forefront endpoint protection 2010 server management', 'sophos anti-virus.app', 'symantec antivirus', 'symantec antivirus.app', 'system center 2012 endpoint protection.app', 'virusbarrier x6.app') group by agent_info_record_id) avn on avn.agent_info_record_id = ai.id left join (select agent_info_record_id, value as sitecode from agent_custom_fields acf left join custom_field_names cfn on cfn.id = acf.fieldid where name='site code') ascd on ascd.agent_info_record_id = ai.id where coalesce(sitecode, ' NONE') = %s order by agentname ",
    prompts=["sitecode"]
),

Report(
    report_id=9,
    name="Core 3: Outdated core apps for a computer",
    description="All core apps installed on a specific computer that do not match these target application versions: Adobe Reader {0} or {1}, Firefox {2}, Flash Player ActiveX {3}, Flash Player Plugin {4}, Java {5}".format(adobe_reader_x_latest, adobe_reader_xi_latest, firefox_latest, flash_player_activex_latest, flash_player_plugin_latest, java_latest),
    columns=["Application Name", "Application Version", "Last Software Scan"],
    sql="select name, version, date_format(convert_tz(lastinstalledsoftwareinfo, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s') as lastinstalledsoftwareinfo from agent_info ai join asset_modification_info ami on ami.agent_info_record_id = ai.id join installed_software_info isi on isi.agent_info_record_id = ai.id join installed_software_titles ist on ist.id = isi.installed_software_titles_record_id where agentname = %s and identificationtype in (2, 3) and ((name like 'adobe reader%%' and version not in ('{0}', '{1}', '{2}')) or (name like 'mozilla firefox%%' and version not in ('{3}')) or (name like 'firefox.app' and version not in ('{3}')) or (name like '%%flash player%%activex' and version not in ('{4}')) or (name like '%%flash player%%plugin' and version not in ('{5}')) or (name like 'java 2%%') or (name like 'java(tm) se runtime environment 6')or (name like 'java(tm) 6%%') or (name like 'java(tm) 7%%') or (name like 'java 7%%' and version not in ('{6}'))) order by name".format(adobe_reader_x_latest, adobe_reader_xi_latest, adobe_reader_xi_latest_mac, firefox_latest, flash_player_activex_latest, flash_player_plugin_latest, java_latest),
    prompts=["agentname"]
),

Report(
    report_id=10,
    name="Core 2: Core app compliance for a site",
    description="All computers in a site that have outdated core apps installed",
    columns=["Computer Name", "Current User", "Platform", "Number of Outdated Core Apps", "Update Java", "Last Software Scan"],
    sql="select agentname, currentuser, enum_value as agentplatform, count(ist.name) as total_outdated_core_apps, if(update_java = 1, 'Yes', 'No') as update_java, date_format(convert_tz(lastinstalledsoftwareinfo, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s') as lastinstalledsoftwareinfo from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id join software_info si on si.agent_info_record_id = ai.id join enum_AgentPlatform eap on eap.enum_key = ai.agentplatform join asset_modification_info ami on ami.agent_info_record_id = ai.id join installed_software_info isi on isi.agent_info_record_id = ai.id join installed_software_titles ist on ist.id = isi.installed_software_titles_record_id left join (select agent_info_record_id, numbervalue as update_java from agent_custom_fields acf left join custom_field_names cfn on cfn.id = acf.fieldid where name='update_java') auj on auj.agent_info_record_id = ai.id where coalesce(agent_site_code, ' NONE') = %s and identificationtype in (2, 3) and ((ist.name like 'adobe reader%%' and version not in ('{0}', '{1}', '{2}')) or (ist.name like 'mozilla firefox%%' and version not in ('{3}')) or (ist.name like 'firefox.app' and version not in ('{3}')) or (ist.name like '%%flash player%%activex' and version not in ('{4}')) or (ist.name like '%%flash player%%plugin' and version not in ('{5}')) or (ist.name like 'java 2%%') or (ist.name like 'java(tm) se runtime environment 6')or (ist.name like 'java(tm) 6%%') or (ist.name like 'java(tm) 7%%') or (ist.name like 'java 7%%' and version not in ('{6}'))) group by agentname order by agentname".format(adobe_reader_x_latest, adobe_reader_xi_latest, adobe_reader_xi_latest_mac, firefox_latest, flash_player_activex_latest, flash_player_plugin_latest, java_latest),
    prompts=["sitecode"],
    link={
        "target_report_id": 9,
        "target_prompt_name": "agentname"
    }
),

Report(
    report_id=11,
    name="02 - Core 1: Core app compliance overview",
    description="All sites with total computer count and compliant computer count; a computer is compliant if all installed core apps match the target application versions",
    columns=["Site", "Total Computers", "Compliant Computers", "Compliance Percentage"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, count(id) as total_computers, count(id) - coalesce(sum(ocai = 1), 0) as total_compliant, round((count(id) - coalesce(sum(ocai = 1), 0)) / count(id) * 100, 2) as compliance_percentage from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join (select distinct agent_info_record_id, true as ocai from installed_software_info isi join installed_software_titles ist on ist.id = isi.installed_software_titles_record_id where identificationtype in (2, 3) and ((name like 'adobe reader%' and version not in ('{0}', '{1}', '{2}')) or (name like 'mozilla firefox%' and version not in ('{3}')) or (name like 'firefox.app' and version not in ('{3}')) or (name like '%flash player%activex' and version not in ('{4}')) or (name like '%flash player%plugin' and version not in ('{5}')) or (name like 'java 2%') or (name like 'java(tm) se runtime environment 6')or (name like 'java(tm) 6%') or (name like 'java(tm) 7%') or (name like 'java 7%' and version not in ('{6}')) )) ocai on ocai.agent_info_record_id = ai.id group by agent_site_code_n order by agent_site_code_n".format(adobe_reader_x_latest, adobe_reader_xi_latest, adobe_reader_xi_latest_mac, firefox_latest, flash_player_activex_latest, flash_player_plugin_latest, java_latest),
    link={
        "target_report_id": 10,
        "target_prompt_name": "sitecode"
    }
),

Report(
    report_id=12,
    name="Enc 3: Encryption method overview",
    description="Count of computers using each encryption method",
    columns=["Encryption Method", "Computer Count"],
    sql="select coalesce(sdw, sdm, fv, fv2, bl1, bl2, ex, ' Not Encrypted') as encryption_method, count(agentname) from agent_info ai join hardware_info hi on hi.agent_info_record_id = ai.id left join enum_MachineModel emm on emm.enum_key = hi.computermodel left join (select agent_info_record_id, 'SecureDoc' as sdw from win_services_info wsi join win_services_servicenames wsn on wsn.id = wsi.win_services_servicenames_record_id where servicename rlike 'winmagic' and status = 4) sdw on sdw.agent_info_record_id = ai.id left join (select agent_info_record_id, 'SecureDoc' as sdm from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'securedocd pid' and numbervalue > - 1) sdm on sdm.agent_info_record_id = ai.id left join (select agent_info_record_id, 'FileVault' as fv from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'filevault 1 accounts' and numbervalue > 0) fv on fv.agent_info_record_id = ai.id left join (select agent_info_record_id, 'FileVault 2' as fv2 from software_info where diskencryptionproductname = 'mac os x filevault 2' and diskencryptionstatus like 'volumes fully encrypted%') fv2 on fv2.agent_info_record_id = ai.id left join (select agent_info_record_id, 'BitLocker' as bl1 from software_info where diskencryptionproductname = 'bitlocker drive encryption driver' and diskencryptionstatus like '%fully encrypted%') bl1 on bl1.agent_info_record_id = ai.id left join (select agent_info_record_id, 'BitLocker' as bl2 from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'bitlocker status' and value like '%[protected]%') bl2 on bl2.agent_info_record_id = ai.id left join (select agent_info_record_id, ' Exempt' as ex from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'encryption exempt' and numbervalue = 1) ex on ex.agent_info_record_id = ai.id where coalesce(emm.enum_value, computermodel) not rlike 'virtual' group by encryption_method order by encryption_method",
    link={
        "target_report_id": 38,
        "target_prompt_name": "encryption_method"
    }
),

Report(
    report_id=13,
    name="04 - Enc 1a: Encryption compliance overview (portable)",
    description="All sites with total portable computer count and encrypted portable computer count",
    columns=["Site", "Total Computers", "Encrypted Computers", "Compliance Percentage"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, count(ai.id) as total_computers, count(coalesce(sdw, sdm, fv, fv2, bl1, bl2, ex)) as encrypted_computers, round((count(coalesce(sdw, sdm, fv, fv2, bl1, bl2, ex)) / count(ai.id)) * 100, 2) as compliance_percentage from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join hardware_info hi on hi.agent_info_record_id = ai.id left join enum_MachineModel emm on emm.enum_key = hi.computermodel left join (select agent_info_record_id, 1 as sdw from win_services_info wsi join win_services_servicenames wsn on wsn.id = wsi.win_services_servicenames_record_id where servicename rlike 'winmagic' and status = 4) sdw on sdw.agent_info_record_id = ai.id left join (select agent_info_record_id, 1 as sdm from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'securedocd pid' and numbervalue > -1) sdm on sdm.agent_info_record_id = ai.id left join (select agent_info_record_id, 1 as fv from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'filevault 1 accounts' and numbervalue > 0) fv on fv.agent_info_record_id = ai.id left join (select agent_info_record_id, 1 as fv2 from software_info where diskencryptionproductname = 'mac os x filevault 2' and diskencryptionstatus like 'volumes fully encrypted%') fv2 on fv2.agent_info_record_id = ai.id left join (select agent_info_record_id, 1 as bl1 from software_info where diskencryptionproductname = 'bitlocker drive encryption driver' and diskencryptionstatus like '%fully encrypted%') bl1 on bl1.agent_info_record_id = ai.id left join (select agent_info_record_id, 1 as bl2 from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'bitlocker status' and value like '%[protected]%') bl2 on bl2.agent_info_record_id = ai.id left join (select agent_info_record_id, 1 as ex from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'encryption exempt' and numbervalue = 1) ex on ex.agent_info_record_id = ai.id where coalesce(enum_value, computermodel) rlike '{0}' group by agent_site_code_n order by agent_site_code_n".format(portable_rlike),
    link={
        "target_report_id": 14,
        "target_prompt_name": "sitecode"
    }
),

Report(
    report_id=14,
    name="Enc 2a: Encryption compliance for a site (portable)",
    description="All portable computers in a site with encryption method for each computer",
    columns=["Computer Name", "Computer Model", "Encryption Method", "Last Heartbeat"],
    sql="select agentname, coalesce(enum_value, computermodel) as computer_model, coalesce(sdw, sdm, fv, fv2, bl1, bl2, ex, ' Not Encrypted') as encryption_method, date_format(convert_tz(lastheartbeat, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s') as lastheartbeat from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join hardware_info hi on hi.agent_info_record_id = ai.id left join enum_MachineModel emm on emm.enum_key = hi.computermodel left join (select agent_info_record_id, 'SecureDoc' as sdw from win_services_info wsi join win_services_servicenames wsn on wsn.id = wsi.win_services_servicenames_record_id where servicename rlike 'winmagic' and status = 4) sdw on sdw.agent_info_record_id = ai.id left join (select agent_info_record_id, 'SecureDoc' as sdm from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'securedocd pid' and numbervalue > -1) sdm on sdm.agent_info_record_id = ai.id left join (select agent_info_record_id, 'FileVault' as fv from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'filevault 1 accounts' and numbervalue > 0) fv on fv.agent_info_record_id = ai.id left join (select agent_info_record_id, 'FileVault 2' as fv2 from software_info where diskencryptionproductname = 'mac os x filevault 2' and diskencryptionstatus like 'volumes fully encrypted%%') fv2 on fv2.agent_info_record_id = ai.id left join (select agent_info_record_id, 'BitLocker' as bl1 from software_info where diskencryptionproductname = 'bitlocker drive encryption driver' and diskencryptionstatus like '%%fully encrypted%%') bl1 on bl1.agent_info_record_id = ai.id left join (select agent_info_record_id, 'BitLocker' as bl2 from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'bitlocker status' and value like '%%[protected]%%') bl2 on bl2.agent_info_record_id = ai.id left join (select agent_info_record_id, ' Exempt' as ex from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'encryption exempt' and numbervalue = 1) ex on ex.agent_info_record_id = ai.id where coalesce(enum_value, computermodel) rlike '{0}' and coalesce(agent_site_code, ' NONE') = %s order by agentname".format(portable_rlike),
    prompts=["sitecode"]
),

Report(
    report_id=15,
    name="Crit 5: Critical update compliance overview for Mac",
    description="All sites with total Mac count and compliant Mac count; sites with no Macs do not appear in this report",
    columns=["Site", "Total Macs", "Compliant Macs", "Compliance Percentage"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, count(ai.id) as total_macs, sum(imcp is null) as compliant_macs, round((sum(imcp is null) / count(ai.id)) * 100, 2) as compliance_percentage from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join (select distinct agent_info_record_id, true as imcp from missing_patches_info where name not rlike '^[abdefghiklnpqrxz]|^c[ahlrz]|^jap|mini|supp|^macb|^mig|^sam|^serb|^serve|^s[lnpuw]|^th[au]|^tu|^uk|^windows [ils]') mcp on mcp.agent_info_record_id = ai.id where agentplatform = 1 group by agent_site_code_n",
    link={
        "target_report_id": 7,
        "target_prompt_name": "sitecode"
    }
),

Report(
    report_id=16,
    name="Apps: Computers with a specific application installed",
    description="All computers with a specific application installed; use % as a wildcard",
    columns=["Site", "Computer Name", "Platform", "App Name", "App Version", "Last Software Scan"],
    sql="select agent_site_code, agentname, enum_value as agentplatform, name, version, date_format(convert_tz(lastinstalledsoftwareinfo, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s') as lastinstalledsoftwareinfo from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join enum_AgentPlatform eap on eap.enum_key = ai.agentplatform left join asset_modification_info ami on ami.agent_info_record_id = ai.id left join installed_software_info isi on isi.agent_info_record_id = ai.id left join installed_software_titles ist on ist.id = isi.installed_software_titles_record_id where identificationtype in (2, 3) and name like %s order by agent_site_code, agentname",
    prompts=["app_name"],
),


Report(
    report_id=17,
    name="Enc 2b: Encryption compliance for a site (non-portable)",
    description="All non-portable computers in a site with encryption method for each computer",
    columns=["Computer Name", "Computer Model", "Encryption Method", "Last Heartbeat"],
    sql="select agentname, coalesce(enum_value, computermodel) as computer_model, coalesce(sdw, sdm, fv, fv2, bl1, bl2, ex, ' Not Encrypted') as encryption_method, date_format(convert_tz(lastheartbeat, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s') as lastheartbeat from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join hardware_info hi on hi.agent_info_record_id = ai.id left join enum_MachineModel emm on emm.enum_key = hi.computermodel left join (select agent_info_record_id, 'SecureDoc' as sdw from win_services_info wsi join win_services_servicenames wsn on wsn.id = wsi.win_services_servicenames_record_id where servicename rlike 'winmagic' and status = 4) sdw on sdw.agent_info_record_id = ai.id left join (select agent_info_record_id, 'SecureDoc' as sdm from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'securedocd pid' and numbervalue > -1) sdm on sdm.agent_info_record_id = ai.id left join (select agent_info_record_id, 'FileVault' as fv from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'filevault 1 accounts' and numbervalue > 0) fv on fv.agent_info_record_id = ai.id left join (select agent_info_record_id, 'FileVault 2' as fv2 from software_info where diskencryptionproductname = 'mac os x filevault 2' and diskencryptionstatus like 'volumes fully encrypted%%') fv2 on fv2.agent_info_record_id = ai.id left join (select agent_info_record_id, 'BitLocker' as bl1 from software_info where diskencryptionproductname = 'bitlocker drive encryption driver' and diskencryptionstatus like '%%fully encrypted%%') bl1 on bl1.agent_info_record_id = ai.id left join (select agent_info_record_id, 'BitLocker' as bl2 from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'bitlocker status' and value like '%%[protected]%%') bl2 on bl2.agent_info_record_id = ai.id left join (select agent_info_record_id, ' Exempt' as ex from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'encryption exempt' and numbervalue = 1) ex on ex.agent_info_record_id = ai.id where coalesce(enum_value, computermodel) not rlike '{0}|virtual' and coalesce(agent_site_code, ' NONE') = %s order by agentname".format(portable_rlike),
    prompts=["sitecode"]
),

Report(
    report_id=18,
    name="04 - Enc 1b: Encryption compliance overview (non-portable)",
    description="All sites with total non-portable computer count and encrypted non-portable computer count",
    columns=["Site", "Total Computers", "Encrypted Computers", "Compliance Percentage"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, count(ai.id) as total_computers, count(coalesce(sdw, sdm, fv, fv2, bl1, bl2, ex)) as encrypted_computers, round((count(coalesce(sdw, sdm, fv, fv2, bl1, bl2, ex)) / count(ai.id)) * 100, 2) as compliance_percentage from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join hardware_info hi on hi.agent_info_record_id = ai.id left join enum_MachineModel emm on emm.enum_key = hi.computermodel left join (select agent_info_record_id, 1 as sdw from win_services_info wsi join win_services_servicenames wsn on wsn.id = wsi.win_services_servicenames_record_id where servicename rlike 'winmagic' and status = 4) sdw on sdw.agent_info_record_id = ai.id left join (select agent_info_record_id, 1 as sdm from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'securedocd pid' and numbervalue > -1) sdm on sdm.agent_info_record_id = ai.id left join (select agent_info_record_id, 1 as fv from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'filevault 1 accounts' and numbervalue > 0) fv on fv.agent_info_record_id = ai.id left join (select agent_info_record_id, 1 as fv2 from software_info where diskencryptionproductname = 'mac os x filevault 2' and diskencryptionstatus like 'volumes fully encrypted%') fv2 on fv2.agent_info_record_id = ai.id left join (select agent_info_record_id, 1 as bl1 from software_info where diskencryptionproductname = 'bitlocker drive encryption driver' and diskencryptionstatus like '%fully encrypted%') bl1 on bl1.agent_info_record_id = ai.id left join (select agent_info_record_id, 1 as bl2 from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'bitlocker status' and value like '%[protected]%') bl2 on bl2.agent_info_record_id = ai.id left join (select agent_info_record_id, 1 as ex from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'encryption exempt' and numbervalue = 1) ex on ex.agent_info_record_id = ai.id where coalesce(enum_value, computermodel) not rlike '{0}|virtual' group by agent_site_code_n order by agent_site_code_n".format(portable_rlike),
    link={
        "target_report_id": 17,
        "target_prompt_name": "sitecode",
    }
),

Report(
    report_id=19,
    name="_ Local admins for a computer",
    description="Users and groups that have local administrative privileges on a computer",
    columns=["Site", "Computer Name", "Local Admins"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, agentname, value from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join (select agent_info_record_id, value from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'local admins') la on la.agent_info_record_id = ai.id"
),

Report(
    report_id=20,
    name="_ Software on a computer",
    description="List of all software installed on a specific computer",
    columns=["Company", "Software Name", "Version", "Installation Date"],
    sql="select company, name, version, date_format(convert_tz(installationdate, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s') from agent_info ai join installed_software_info isi on isi.agent_info_record_id = ai.id join installed_software_titles ist on ist.id = isi.installed_software_titles_record_id where agentname = %s and identificationtype in (2, 3) order by name",
    prompts=["agentname"]
),

Report(
    report_id=21,
    name="Priv 2: Current users with admin privileges for a site",
    description="All users currently logged on to computers at a site and whether they have admin privileges",
    columns=["Computer Name", "Operating System", "Last Logged On User", "Current User", "Current User Is Admin", "Last Heartbeat"],
    sql="select agentname, enum_value as os_platform, lastloggedinshortusername, currentuser, if(currentuserisadmin, 'Yes', 'No') as current_user_is_admin, date_format(convert_tz(lastheartbeat, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s') as lastheartbeat from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join software_info si on si.agent_info_record_id = ai.id left join enum_OSPlatform eosp on eosp.enum_key = si.osplatform where coalesce(agent_site_code, ' NONE') = %s order by agentname",
    prompts=["agent_site_code"]
),

Report(
    report_id=22,
    name="Crit 4: Macs with OS updates turned off",
    description="All Macs with OS updates turned off",
    columns=["Site", "Computer Name", "Current User", "Last Heartbeat"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, agentname, currentuser, date_format(convert_tz(lastheartbeat, '+00:00', 'system'), '%Y-%m-%d %H:%i:%s') as lastheartbeat from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join software_info si on si.agent_info_record_id = ai.id where agentplatform = 1 and checkapplesoftwarepatches = 0 order by agent_site_code_n, agentname"
),

Report(
    report_id=23,
    name="Inv 6: Duplicate computer names",
    description="A list of computer names that are used by more than one computer in the database",
    columns=["Computer Name", "Number of Computers"],
    sql="select agentname, count(id) as num from agent_info group by agentname having num > 1"
),

Report(
    report_id=24,
    name="_ ITS computers with CrashPlan installed",
    description="All computers in ITS sites with CrashPlan installed",
    columns=["Site", "Computer Name", "Platform", "App Name", "App Version", "Last Software Scan"],
    sql="select agent_site_code, agentname, enum_value, ist.name, version, date_format(convert_tz(lastinstalledsoftwareinfo, '+00:00', 'system'), '%Y-%m-%d %H:%i:%s') as lastinstalledsoftwareinfo from agent_info ai join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id join enum_AgentPlatform eap on eap.enum_key = ai.agentplatform join asset_modification_info ami on ami.agent_info_record_id = ai.id join installed_software_info isi on isi.agent_info_record_id = ai.id join installed_software_titles ist on ist.id = isi.installed_software_titles_record_id where agent_site_code like 'its%' and identificationtype in (2, 3) and ist.name like '%crashplan%' order by agent_site_code, agentname",
),

Report(
    report_id=25,
    name="Priv 1: Admin privileges overview",
    description="All sites with percentage of computers that have an admin user currently logged on",
    columns=["Site", "Total Computers", "Admin Logged On", "Percentage With Admin Logged On"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, count(ai.id) as total_computers, sum(currentuserisadmin) as admin_users, round((sum(currentuserisadmin) / count(ai.id)) * 100, 2) as admin_percentage from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join software_info si on si.agent_info_record_id = ai.id group by agent_site_code_n order by agent_site_code_n",
    link={
        "target_report_id": 21,
        "target_prompt_name": "agent_site_code",
    }
),

Report(
    report_id=26,
    name="_ Hardware: Latitude E6420 with old BIOS",
    description="All Latitude E6420 computers with BIOS that is not A17",
    columns=["Site", "Computer Name", "Current User", "Model", "BIOS Version", "Last Inventory"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, agentname, currentuser, computermodel, biosversion, date_format(convert_tz(lastinventoryupdate, '+00:00', 'system'), '%Y-%m-%d %H:%i:%s') as last_inventory from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id join hardware_info hi on hi.agent_info_record_id = ai.id join software_info si on si.agent_info_record_id = ai.id join asset_modification_info ami on ami.agent_info_record_id = ai.id where computermodel = 'latitude e6420' and biosversion not in ('a17') order by agent_site_code_n, agentname"
),

Report(
    report_id=27,
    name="_ Java on Macs overview",
    description="Count of how many Macs have each version of Java installed",
    columns=["Java Version", "Number of Macs"],
    sql="select value as version, count(*) as computer_count from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'java version' group by value order by value",
    link={
        "target_report_id": 28,
        "target_prompt_name": "version",
    }
),

Report(
    report_id=28,
    name="_ Macs with a specific version of Java installed",
    description="Macs with a specific verson of Java installed",
    columns=["Site", "Computer Name", "Last Inventory"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, agentname, date_format(convert_tz(lastcustomfieldinfo, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s') as lastinventory from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id join asset_modification_info ami on ami.agent_info_record_id = ai.id join agent_custom_fields acf on acf.agent_info_record_id = ai.id join custom_field_names cfn on cfn.id = acf.fieldid where name = 'java version' and value = %s order by agent_site_code_n, agentname",
    prompts=["version"]
),

Report(
    report_id=29,
    name="Inv 3: Computers not checking in",
    description="Computers that have not sent a heartbeat for 1 month",
    columns=["Site", "Computer Name", "Last Known User", "Last Heartbeat"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, agentname, currentuser, date_format(convert_tz(lastheartbeat, '+00:00', 'system'), '%Y-%m-%d %H:%i:%s') as lastheartbeat from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join software_info si on si.agent_info_record_id = ai.id where lastheartbeat < now() - interval 1 month order by agent_site_code_n, agentname",
),

Report(
    report_id=30,
    name="_ Java on Windows overview",
    description="Count of how many Windows computers have each version of Java installed",
    columns=["Java Version", "Number of Computers"],
    sql="select version, count(*) as computer_count from installed_software_info isi join installed_software_titles ist on ist.id = isi.installed_software_titles_record_id where identificationtype = 3 and name regexp '^java( 2 r| 7|[(]tm[)] (6|7|se r))' group by version order by version",
    link={
        "target_report_id": 31,
        "target_prompt_name": "version",
    }
),

Report(
    report_id=31,
    name="_ Windows computers with a specific version of Java installed",
    description="Windows computers with a specific version of Java installed",
    columns=["Site", "Computer Name", "Last Known User", "Software Name", "Software Version", "Last Software Scan"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, agentname, currentuser, name, version, date_format(convert_tz(lastinstalledsoftwareinfo, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s') as lastsoftwarescan from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join software_info si on si.agent_info_record_id = ai.id join asset_modification_info ami on ami.agent_info_record_id = ai.id join installed_software_info isi on isi.agent_info_record_id = ai.id join installed_software_titles ist on ist.id = isi.installed_software_titles_record_id where identificationtype = 3 and name regexp '^java( 2 r| 7|[(]tm[)] (6|7|se r))' and version = %s order by agent_site_code_n, agentname, name",
    prompts=["version"]
),

Report(
    report_id=32,
    name="_ Updates installed in the last 7 days",
    description="Number of updates installed in the last 7 days",
    columns=["Windows Updates", "Mac OS X Updates", "Third Party Updates", "Computers Updated"],
    sql="select sum(iswindowspatch) as windows_updates, sum(ismacospatch) as mac_os_x_update, sum(if(iswindowspatch + ismacospatch = 0, 1, 0)) as third_party_updates, count(distinct agent_info_record_id) as computers_updated from sd_installation_status sis join sd_packages sp on sp.id = sis.sd_package_record_id where status = 5 and logdate > subdate(now(), 7)"
),

Report(
    report_id=33,
    name="Inv 5: Computers without a Site",
    description="Computers that do not have a Site set",
    columns=["Computer Name", "Computer Platform", "Client Site", "Current User", "Computer OU", "Last Heartbeat"],
    sql="select agentname, enum_value, userinfo0, currentuser, ad_machineoupath, date_format(convert_tz(lastheartbeat, '+00:00', 'system'), '%Y-%m-%d %H:%i:%s') as lastheartbeat from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id join software_info si on si.agent_info_record_id = ai.id join enum_AgentPlatform eap on eap.enum_key = ai.agentplatform where agent_site_code is null order by agentname"
),

Report(
    report_id=34,
    name="Apps: Computers with multiple versions of Adobe Reader",
    description="Windows computers that report more than one version of Adobe Reader installed",
    columns=["Computer Name"],
    sql="select agentname from installed_software_info isi join installed_software_titles ist on ist.id = isi.installed_software_titles_record_id join agent_info ai on ai.id = isi.agent_info_record_id where name like 'adobe reader%' and identificationtype = 3 group by agent_info_record_id having count(agent_info_record_id) > 1 order by agentname"
),

Report(
    report_id=35,
    name="_ Java installations on Windows at a site",
    description="Windows computers at a particular site with Java installed",
    columns=["Computer Name", "Java Version", "Last Software Scan", "Last Heartbeat"],
    sql="select agentname, name, date_format(convert_tz(lastinstalledsoftwareinfo, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s'), date_format(convert_tz(lastheartbeat, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s') from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id join asset_modification_info ami on ami.agent_info_record_id = ai.id join installed_software_info isi on isi.agent_info_record_id = ai.id join installed_software_titles ist on ist.id = isi.installed_software_titles_record_id where agent_site_code = %s and identificationtype = 3 and (name like 'java(tm)%%' or name like 'java 7%%' or name like 'j2se%%') order by agentname, name",
    prompts=["sitecode"]
),

Report(
    report_id=36,
    name="_ Java installations on Mac OS X at a site",
    description="Mac OS X computers at a particular site with Java installed",
    columns=["Computer Name", "Java Version", "Last Java Version Scan", "Last Heartbeat"],
    sql="select agentname, java_version, date_format(convert_tz(java_modified, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s'), date_format(convert_tz(lastheartbeat, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s') from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id join asset_modification_info ami on ami.agent_info_record_id = ai.id join (select agent_info_record_id, value as java_version, last_modified as java_modified from agent_custom_fields acf left join custom_field_names cfn on cfn.id = acf.fieldid where name = 'java version') java on java.agent_info_record_id = ai.id where agent_site_code = %s order by agentname, java_version",
    prompts=["sitecode"]
),

Report(
    report_id=37,
    name="Apps: Computers missing Office 2010 SP2",
    description="These computers have Office 2010 installed but do not have SP2 (14.0.7012.1000)",
    columns=["Site", "Computer Name", "Platform", "Software Name", "Software Version", "Last Software Scan"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, agentname, if(agentplatform = 1, 'Mac OS X', 'Windows') as agentplatform, name, version, date_format(convert_tz(lastinstalledsoftwareinfo, '+00:00', 'system'), '%Y-%m-%d %H:%i:%s') as lastsoftwarescan from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id join asset_modification_info ami on ami.agent_info_record_id = ai.id join installed_software_info isi on isi.agent_info_record_id = ai.id join installed_software_titles ist on ist.id = isi.installed_software_titles_record_id where name = 'outlook.exe' and version like '14.%' and version not like '14.0.7%' order by agent_site_code_n, agentname"
),

Report(
    report_id=38,
    name="Enc 4: Computers with a specific encryption method",
    description="All computers that are encrypted with the specified encryption method",
    columns=["Site", "Computer Name", "Computer Model", "Encryption Method", "Last Heartbeat"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, agentname, coalesce(emm.enum_value, computermodel) as computer_model, coalesce(sdw, sdm, fv, fv2, bl1, bl2, ex, ' Not Encrypted') as encryption_method, date_format(convert_tz(lastheartbeat, '+00:00', 'system'), '%%Y-%%m-%%d %%H:%%i:%%s') as lastheartbeat from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id join hardware_info hi on hi.agent_info_record_id = ai.id left join enum_MachineModel emm on emm.enum_key = hi.computermodel left join (select agent_info_record_id, 'SecureDoc' as sdw from win_services_info wsi join win_services_servicenames wsn on wsn.id = wsi.win_services_servicenames_record_id where servicename rlike 'winmagic' and status = 4) sdw on sdw.agent_info_record_id = ai.id left join (select agent_info_record_id, 'SecureDoc' as sdm from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'securedocd pid' and numbervalue > -1) sdm on sdm.agent_info_record_id = ai.id left join (select agent_info_record_id, 'FileVault' as fv from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'filevault 1 accounts' and numbervalue > 0) fv on fv.agent_info_record_id = ai.id left join (select agent_info_record_id, 'FileVault 2' as fv2 from software_info where diskencryptionproductname = 'mac os x filevault 2' and diskencryptionstatus like 'volumes fully encrypted%%') fv2 on fv2.agent_info_record_id = ai.id left join (select agent_info_record_id, 'BitLocker' as bl1 from software_info where diskencryptionproductname = 'bitlocker drive encryption driver' and diskencryptionstatus like '%%fully encrypted%%') bl1 on bl1.agent_info_record_id = ai.id left join (select agent_info_record_id, 'BitLocker' as bl2 from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'bitlocker status' and value like '%%[protected]%%') bl2 on bl2.agent_info_record_id = ai.id left join (select agent_info_record_id, ' Exempt' as ex from agent_custom_fields acf join custom_field_names cfn on cfn.id = acf.fieldid where name = 'encryption exempt' and numbervalue = 1) ex on ex.agent_info_record_id = ai.id where coalesce(emm.enum_value, computermodel) not rlike 'virtual' and coalesce(sdw, sdm, fv, fv2, bl1, bl2, ex, ' Not Encrypted') = %s order by agent_site_code_n, agentname",
    prompts=["encryption_method"]
),

Report(
    report_id=39,
    name="_ Windows computers without Configuration Manager Client",
    description="All Windows computers that do not have a Configuration Manager Client installed",
    columns=["Site", "Computer Name", "Last Software Scan"],
    sql="select coalesce(agent_site_code, ' NONE') as agent_site_code_n, agentname, date_format(convert_tz(lastinstalledsoftwareinfo, '+00:00', 'system'), '%Y-%m-%d %H:%i:%s') as lastinstalledsoftwareinfo from agent_info ai left join v_agent_site_codes vasc on vasc.agent_info_record_id = ai.id left join asset_modification_info ami on ami.agent_info_record_id = ai.id where agent_site_code not like 'uo%' and agentplatform = 2 and ai.id not in (select agent_info_record_id from installed_software_info isi join installed_software_titles ist on ist.id = isi.installed_software_titles_record_id where name = 'configuration manager client' and version like '5%') order by agent_site_code_n, agentname"
)

]
