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
