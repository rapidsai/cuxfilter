# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

# Standard library imports
import sys
import types

# Bokeh imports
from bokeh.core.enums import enumeration

import logging

log = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Copyright (c) 2012 - 2019, Anaconda, Inc., and Bokeh Contributors.
# All rights reserved.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
""" Pre-configured tile sources for common third party tile services.


Attributes:

    .. bokeh-enum:: Vendors
        :module: bokeh.tile_providers

    get_provider
        Use this function to retrieve an instance of a custom mapbox tile
        provider.

        Args:
            provider_name (Union[str, Vendors])
                Name of the tile provider to supply.
                Use tile_providers.Vendors enum, or the name of a provider as
                string

        Returns:
            WMTSTileProviderSource: The desired tile provider instance

        Raises:
            ValueError, if the provider can not be found
            ValueError, if the attribution for that provider can not be found


        Example:

            .. code-block:: python

                    >>> from bokeh.tile_providers import get_provider, Vendors
                    >>> get_provider(Vendors.MAPBOX_DARK, access_token='')
                    <class 'bokeh.models.tiles.WMTSTileSource'>
                    >>> get_provider('MAPBOX_LIGHT', access_token='')
                    <class 'bokeh.models.tiles.WMTSTileSource'>

    MAPBOX_DARK
        Tile Source for MAPBOX with a dark theme

        Warns:
            BokehDeprecationWarning: Deprecated in bokeh 1.1.0. Use
            get_provider instead

        .. raw:: html

            <img src="https://api.mapbox.com/styles/v1/mapbox/dark-
            /tiles/14/2627/6331@2x?access_token=<access_token>" />

    STAMEN_TONER_LABELS
        Tile Source for MAPBOX with a light theme

        Warns:
            BokehDeprecationWarning: Deprecated in bokeh 1.1.0. Use
            get_provider instead

        .. raw:: html

            <img src="https://api.mapbox.com/styles/v1/mapbox/light-v10/tiles
            /14/2627/6331@2x?access_token=<access_token>" />

Additional information available at:

* MAPBOX tile service - https://docs.mapbox.com/studio-manual/
reference/tilesets/

"""


# Can be removed in bokeh 2.0
def _make_deprecated_property(name):
    def deprecated_property_tile(self):
        from bokeh.util.deprecation import deprecated

        deprecated(
            since_or_msg=(1, 1, 0),
            old=name,
            new="get_provider(Vendors.%s)" % name,
        )
        return self.get_provider(provider_name=name)

    func = property(deprecated_property_tile)
    return func


class _TileProvidersModule(types.ModuleType):
    _MAPBOX_ATTRIBUTION = (
        'Map tiles by <a href="https://mapbox.com">MAPBOX</a>'
    )

    _SERVICE_URLS = dict(
        MAPBOX_DARK=(
            "https://api.mapbox.com/styles/v1/mapbox/"
            "dark-v10/tiles/{z}/{x}/{y}@2x?access_token="
        ),
        MAPBOX_LIGHT=(
            "https://api.mapbox.com/styles/v1/mapbox/"
            "light-v10/tiles/{z}/{x}/{y}@2x?access_token="
        ),
    )

    Vendors = enumeration("MAPBOX_DARK", "MAPBOX_LIGHT", case_sensitive=True)

    def get_provider(self, provider_name, access_token=None):
        from bokeh.models.tiles import WMTSTileSource

        if isinstance(provider_name, WMTSTileSource):
            # This allows `get_provider(CARTODBPOSITRON)` to work
            if provider_name.startswith("MAPBOX"):
                if access_token is None:
                    raise ValueError("provide access token for MAPBOX tiles")
                return WMTSTileSource(
                    url=provider_name.url + str(access_token),
                    attribution=provider_name.attribution,
                )

        selected_provider = provider_name.upper()

        if selected_provider not in self.Vendors:
            raise ValueError("Unknown tile provider %s" % provider_name)

        url = self._SERVICE_URLS[selected_provider]
        if selected_provider.startswith("MAPBOX"):
            attribution = self._MAPBOX_ATTRIBUTION
            if access_token is None:
                raise ValueError("provide access token for MAPBOX tiles")
            return WMTSTileSource(
                url=url + str(access_token), attribution=attribution
            )
        else:
            raise ValueError(
                "Can not retrieve attribution for %s" % selected_provider
            )

    # Properties --------------------------------------------------------------

    MAPBOX_DARK = _make_deprecated_property(Vendors.MAPBOX_DARK)
    MAPBOX_LIGHT = _make_deprecated_property(Vendors.MAPBOX_LIGHT)


# ----------------------------------------------------------------------------
# Code
# -----------------------------------------------------------------------------

_mod = _TileProvidersModule(str("cuxfilter.assets.custom_tiles"))
_mod.__doc__ = __doc__
_mod.__all__ = ("get_provider", "Vendors")

sys.modules["cuxfilter.assets.custom_tiles"] = _mod
del _mod, sys, types, _make_deprecated_property
