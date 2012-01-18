# Copyright (c) 2012, Braiden Kindt.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# 
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
# 
#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS ''AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging

from gant.ant_core import MessageType, RadioEventType, ChannelEventType, Listener, Dispatcher

_log = logging.getLogger("gant.ant_workflow")

def execute(dispatcher, state):
    ctx = Context(dispatcher)
    workflow = Workflow(state)
    if workflow.enter(ctx) not in (ERROR_STATE, FINAL_STATE):
        dispatcher.loop(WorkflowListener(workflow, ctx))
    assert workflow.state != ERROR_STATE
    return ctx

def chain(*states):
    for (s1, s2) in zip(states[:-1], states[1:]):
        s1.next_state = s2
    return s1


class Event(object):
    
    source = None

    def __str__(self):
        return str(self.__dict__)


class WorkflowListener(Listener):

    def __init__(self, workflow, context):
        self.workflow = workflow
        self.context = context

    def on_message(self, dispatcher, message):
        event = Event()
        event.source = Dispatcher
        (event.msg_id, event.msg_args) = message
        state = self.workflow.accept(self.context, event)
        if state not in (ERROR_STATE, FINAL_STATE):
            return True


class State(object):

    next_state = None

    def __init__(self, name=None):
        if name: self.name = name

    def enter(self, context):
        pass

    def accept(self, context, event):
        return self.next_state

    def __str__(self):
        try: return self.name
        except AttributeError: return self.__class__.__name__

ERROR_STATE = State("ERROR_STATE")
FINAL_STATE = State("FINAL_STATE")
State.next_state = FINAL_STATE


class Context(object):
    
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def send(self, msg_id, *args):
        self.dispatcher.send(msg_id, *args)


class Workflow(State):

    def __init__(self, initial_state):
        self.initial_state = initial_state
        self.state = initial_state

    def enter(self, context):
        _log.debug("Workflow(%s) START: %s" % (str(self), str(self.initial_state)))
        return self.transition(context, self.initial_state.enter(context))

    def accept(self, context, event):
        _log.debug("Workflow(%s) EVENT: %s" % (str(self), str(event)))
        return self.transition(context, self.state.accept(context, event))
    
    def transition(self, context, state):
        while state is not None:
            _log.debug("Workflow(%s) TRANSITION: %s => %s" % (str(self), str(self.state), str(state)))
            self.state = state
            state = state.enter(context)
        if self.state is ERROR_STATE:
            return ERROR_STATE
        elif self.state is FINAL_STATE:
            return self.next_state
            

# vim: et ts=4 sts=4
