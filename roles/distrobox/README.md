Role Name
=========

Configure distrobox container definitions and create containers using
`distrobox assemble`.

Requirements
------------

Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here. For instance, if the role uses the EC2 module, it may be a good idea to mention in this section that the boto package is required.

Role Variables
--------------

- `distrobox_dir`: Base directory for distrobox files.
- `distrobox_config`: Directory where ini files are written.
- `distrobox_home`: Base home directory for containers.
- `distrobox_vms`: Map of distrobox definitions used to render ini files.

Behavior
--------

- Writes one ini file per entry in `distrobox_vms`.
- Creates containers with `distrobox assemble create --file <ini>`.
- For clones, the source container is created and started at least once,
  stopped for the clone operation, and then its prior running state is
  restored afterward.

Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

    - hosts: servers
      roles:
        - { role: distrobox }

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
