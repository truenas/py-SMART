
Version 1.1.0
=============
- Minnor fixes
- **Breaking changes**
    - **Typing**:
        - Tests and attributes have been typed. This may cause some exceptions if you have been attached to the "everything is a string" previously philosophy.
        - Some attributes have been kept back for compatibility but others (like num) have been directly converted into int. Test everything after the upgrade
        - Other typing changes migh take place in the future when it is confirmed that smartctl always use a fixed time instead "anything" (str for us).
    - **device.tests**: Now returns empty list instead of None when there is no tests present

Version 1.0.6
=============
- This release contains minnor changes and upgrades to support python 3.8/9/10 as other other mithor improvements
- It contains all the commits on TRUENAS/pySMART from 9/8/2019 to this version tag.

Version 1.0.0
=============
- This release contains all the commits on TRUENAS/pySMART from 11/6/2015 to 9/8/2019.
- This mostly adds multiplatform support for freebsd and many other interesting improvements

