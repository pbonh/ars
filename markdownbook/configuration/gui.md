# GUI

This will configure KDE Workspaces and Activities as specified by the user. Defaults are available.

Example Yaml Config(user_kde.yml):
```yaml
---
kwin_rules_web_right_23:
  position: "1035,4"
  size: "2376,1432"
kwin_activities:
  browse:
    name: "Browse"
    description: "Web Browse & Research"
    icon: "com.brave.Browser"
    uuid: "240d6a84-dda7-4e1f-9e0c-ab1a9585d939"
kwin_rules:
  brave:
    group: "207e083a-eb97-47f1-81ef-172cc820c3c2"
    Description: "Brave: Browser"
    activity: "{{ kwin_activities['browse']['uuid'] }}"
    activityrule: "3"
    position: "{{ kwin_rules_web_right_23['position'] }}"
    positionrule: "3"
    size: "{{ kwin_rules_web_right_23['size'] }}"
    sizerule: "3"
    windowrole: "browser"
    windowrolematch: "1"
    wmclass: "Brave-browser"
    wmclassmatch: "2"
```

Run this command to apply the workspace & activity settings specified above:

```bash
ansible-pull -U https://github.com/pbonh/ars.git kde.yml --tags "kwin" --skip-tags "install" -e "@user_kde.yml"
```
