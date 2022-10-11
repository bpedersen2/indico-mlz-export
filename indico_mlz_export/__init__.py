from indico.modules.events.settings import EventSettingsProxy
from indico.util.i18n import make_bound_gettext

from indico.core import signals
from indico.modules.events.features.base import EventFeature

_ = make_bound_gettext('mlzexport')

mlzexport_event_settings = EventSettingsProxy('mlzexport', {
    'veranstaltungsid': None,
})



@signals.event.get_feature_definitions.connect
def _get_feature_definitions(sender, **kwargs):
    return FZJExportFeature

class FZJExportFeature(EventFeature):
    name = 'fzjexport'
    friendly_name = _('FZJ Export')
    requires = {'registration'}
    description = _('Gives event managers the opportunity to export FZJ formatted data.')

    @classmethod
    def enabled(cls, event, cloning):
        for setting in (
                'veranstaltungsid',
        ):
            if cloning or mlzexport_event_settings.get(event, setting) is None:
                value = ''
                mlzexport_event_settings.set(event, setting, value)

