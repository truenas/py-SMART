from typing import Optional
from abc import ABC, abstractmethod


class CommonIface (ABC):
    """This class will represent the common interface for all supported interfaces.
    """

    @property
    @abstractmethod
    def temperature(self) -> Optional[int]:
        """Returns the temperature of the disk in Celsius degrees

        Returns:
            int: The temperature of the disk in Celsius degrees
        """
        return None

    @property
    @abstractmethod
    def physical_sector_size(self) -> int:
        """Returns the physical sector size of the disk in bytes.
            If unknown, 512 bytes will be returned as default.

        Returns:
            int: The physical sector size of the disk in bytes
        """
        return 512

    @property
    @abstractmethod
    def logical_sector_size(self) -> int:
        """Returns the logical sector size of the disk in bytes.
            If unknown, returns the physical sector size.

        Returns:
            int: The logical sector size of the disk in bytes
        """
        return self.physical_sector_size
