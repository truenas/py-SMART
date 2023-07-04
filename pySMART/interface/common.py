from typing import Optional


class CommonIface (object):
    """This class will represent the common interface for all supported interfaces.
    """

    @property
    def temperature(self) -> Optional[int]:
        """Returns the temperature of the disk in Celsius degrees

        Returns:
            int: The temperature of the disk in Celsius degrees
        """
        return None
