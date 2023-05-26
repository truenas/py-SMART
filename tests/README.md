**Setting Up Single Tests**
===========================

To include tests for the project, please follow the instructions below:

1. Create a new folder for your tests under `tests/singletests`, like `tests/singletests/nvme_8`. The name of the folder should be descriptive of the test you're adding. For example, if you're adding a test for NVMe devices, you can name the folder `nvme_x` where `x` is the number of the test.

2. Inside the test folder, add a file named `device.json` and include the necessary information.

   The `device.json` file should have the following structure:

   ```json
   {
       "name": "/dev/nvme0"
   }
   ```

   This indicates that your device is named `/dev/nvme0`. However, if you know the interface type of the device and want to skip the initial identification call, you can include the interface type as well:

   ```json
   {
       "name": "/dev/nvme0",
       "interface": "nvme"
   }
   ```

   Please note that this alone won't be sufficient to pass the tests. The tests check if `pysmart` reads the data correctly. To achieve that, there is another field called `"values"` in the `device.json` file. While you can try to fill in the values manually, it is not recommended. Instead, you should generate the `device.json` file using the `gen_devicejson.py` script located in the tests folder. Make sure to verify the contents of `device.json` manually, especially before making any commits, and ensure that other `device.json` files from different tests have not been incorrectly modified.

3. Each test should have output files for each `smartctl` call made by `pysmart`. The file naming format is as follows:

   - For a `smartctl` call such as `smartctl -d nvme --all /dev/nvme0`, replace any problematic characters (e.g., whitespaces and slashes `/`) with an underscore `_`.
   - For the example above, the expected file name for the dataset should be `_-d_nvme_--all__dev_nvme0`.

   If you're unsure about which files you need, you can run your test. If any additional files are required, the test will raise an exception indicating the name of the file it expects, along with the underlying `smartctl` call it needs.

Please make sure to follow these guidelines when adding new tests. It will ensure that the tests are properly organized and executed, making it easier for future developers to understand and contribute to the project.