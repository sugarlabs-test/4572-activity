import olpcgames,traceback,logging,pygame
from olpcgames import mesh,textsprite,eventwrap
from olpcgames.util import get_traceback

log = logging.getLogger('participantwatcher')
log.setLevel(logging.DEBUG)

class ParticipantWatcher(object):
    """Simple class to watch for changes to participants and track set"""
    def __init__( self, groups = () ):
        """Initialize the ParticipantWatcher's internal structures"""
        self._buddies = {}
        self.groups = list( groups )
    def process( self, event ):
        """Process any relevant incoming network events"""
        if event.type == olpcgames.PARTICIPANT_ADD:
            # create a new participant display value...
            current = self._buddies.get( event.handle )
            if not current:
                if current is False:
                    self.removeBuddy( current )
                else:
                    def on_buddy( buddy, event=event ):
                        """Process update from the network telling us about a buddy
                        
                        Note: this function runs in the wrapper's thread, *not* the Pygame thread!"""
                        self.addBuddy( event.handle, buddy )
                    mesh.lookup_buddy( event.handle, on_buddy )
        elif event.type == olpcgames.PARTICIPANT_REMOVE:
            if not self.removeBuddy( event.handle ):
                # race condition, need to block new/upcoming elements...
                self._buddies[ event.handle ] = False
        return False # we haven't consumed the event...
    def addBuddy( self, handle, buddy ):
        """Add a new buddy to internal structures
        
        Note: this is called in the GObject thread!
        """
        try:
            current = self._buddies.get( handle )
            if current is False:
                self.removeBuddy( handle )
                return # we left before we got our metadata
            text = textsprite.TextSprite(
                text = buddy.props.nick,
                color = (255,255,255),
                size = 11,
            )
            self._buddies[ handle ] = (buddy, text)
            for group in self.groups:
                group.add( text )
            #log.info( '''Created text for buddy: %s (%s)''', buddy.props.nick, handle )
            # send event to trigger a rendering/processing cycle...
            eventwrap.post(
                eventwrap.Event(
                    pygame.USEREVENT,
                    code = 1,
                )
            )
            #log.debug( 'Sent user event' )
        except Exception, err:
            log.error( """Failure setting up buddy %s: %s""", buddy, get_traceback( err ) )
        
    def removeBuddy( self,handle ):
        """Remove this buddy from all internal structures"""
        current = self._buddies.get( handle )
        if current:
            (buddy,text) = current 
            for group in self.groups:
                group.remove( text )
        try:
            del self._buddies[ handle ] 
        except KeyError, err:
            pass
        return current

    def layout( self, screenRect ):
        """Layout the buddies in a column down the right side of the screen
        
        Create a second column if we fill up the first column
        """
        #log.info( 'doing layout: %s', self._buddies )
        buddiesSorted = sorted( [
            (buddy.props.nick, (handle,(buddy,text)))
            for (handle,(buddy,text)) in self._buddies.items()
        ])
        if buddiesSorted:
            current = buddiesSorted[0][1][1][1] # text widget of the first item
            current.rect.topright = screenRect.move( -5, 5 ).topright
            minLeft = current.rect.left
            for (nick,(handle,(buddy,text))) in buddiesSorted[1:]:
                #log.info( 'Arranging nickname %s', nick )
                text.rect.right = current.rect.right 
                text.rect.top = current.rect.bottom + 5
                if text.rect.bottom > screenRect.bottom:
                    #log.info( 'Passed end of screen' )
                    text.rect.right = minLeft - 5
                    text.rect.top = 5
                current = text 
                minLeft = min( (minLeft, current.rect.left ))
