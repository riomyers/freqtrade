"""
This module loads custom exchanges
"""
import logging

from freqtrade.exchange import Exchange, MAP_EXCHANGE_CHILDCLASS
import freqtrade.exchange as exchanges
from freqtrade.resolvers import IResolver

logger = logging.getLogger(__name__)


class ExchangeResolver(IResolver):
    """
    This class contains all the logic to load a custom exchange class
    """

    __slots__ = ['exchange']

    def __init__(self, exchange_name: str, config: dict) -> None:
        """
        Load the custom class from config parameter
        :param config: configuration dictionary
        """
        # Map exchange name to avoid duplicate classes for identical exchanges
        exchange_name = MAP_EXCHANGE_CHILDCLASS.get(exchange_name, exchange_name)
        exchange_name = exchange_name.title()
        try:
            self.exchange = self._load_exchange(exchange_name, kwargs={'config': config})
        except ImportError:
            logger.info(
                f"No {exchange_name} specific subclass found. Using the generic class instead.")
        if not hasattr(self, "exchange"):
            self.exchange = Exchange(config)

    def _load_exchange(
            self, exchange_name: str, kwargs: dict) -> Exchange:
        """
        Loads the specified exchange.
        Only checks for exchanges exported in freqtrade.exchanges
        :param exchange_name: name of the module to import
        :return: Exchange instance or None
        """

        try:
            ex_class = getattr(exchanges, exchange_name)

            exchange = ex_class(kwargs['config'])
            if exchange:
                logger.info(f"Using resolved exchange '{exchange_name}'...")
                return exchange
        except AttributeError:
            # Pass and raise ImportError instead
            pass

        raise ImportError(
            f"Impossible to load Exchange '{exchange_name}'. This class does not exist "
            "or contains Python code errors."
        )
