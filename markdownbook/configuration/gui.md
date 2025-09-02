# GUI

This will configure KDE Workspaces and Activities as specified by the user. Defaults are available.

Example Yaml Config(user_kde.yml):
```yaml
---
kwin_rules_web_left_23: 
  position: "48,4"
  size: "983,1432"
kwin_rules_web_right_23:
  position: "1035,4"
  size: "2376,1432"
kwin_activities:
  browse:
    name: "Browse"
    description: "Web Browse & Research"
    icon: "com.opera.Opera"
    uuid: "240d6a84-dda7-4e1f-9e0c-ab1a9585d939"
kwin_rules:
  opera:
    group: "3c93494e-08c5-4fba-a3b8-1dacfa6d1d36"
    Description: "Opera: Browser"
    activity: "{{ kwin_activities['browse']['uuid'] }}"
    position: "{{ kwin_rules_web_right_23['position'] }}"
    size: "{{ kwin_rules_web_right_23['size'] }}"
    activityrule: "3"
    positionrule: "3"
    sizerule: "3"
    wmclass: "Opera"
    wmclassmatch: "2"
    ignoregeometry: "true"
    ignoregeometryrule: "3"
  thunderbird:
    group: "6d7f8fa9-b0ef-4ed7-9832-2c223e2a78df"
    Description: "Thunderbird: Email"
    activity: "{{ kwin_activities['browse']['uuid'] }}"
    position: "{{ kwin_rules_web_left_23['position'] }}"
    size: "{{ kwin_rules_web_left_23['size'] }}"
    activityrule: "3"
    positionrule: "3"
    sizerule: "3"
    wmclass: "org.mozilla.Thunderbird"
    wmclassmatch: "2"
    ignoregeometry: "true"
    ignoregeometryrule: "3"
```

Run this command to apply the workspace & activity settings specified above:

```bash
ansible-pull -U https://github.com/pbonh/ars.git kde.yml --tags "kwin" --skip-tags "install" -e "@user_kde.yml"
```
