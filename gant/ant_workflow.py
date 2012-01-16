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

def execute(dispatcher, workflow):
    ctx = Context(dispatcher)
    if workflow.enter(ctx, INITIAL_STATE) not in (ERROR_STATE, FINAL_STATE):
        dispatcher.loop(WorkflowListener(workflow))


class Event(object):
    
    source = None


class WorkflowListener(Listener):

    def __init__(self, workflow):
        self.workflow = workflow

    def on_message(self, dispatcher, message):
        context = Context(dispatcher)
        event = Event()
        event.source = Dispatcher
        (event.msg_id, event.msg_args) = message
        state = self.workflow.accept(context, event)
        if state not in (ERROR_STATE, FINAL_STATE):
            return True


class State(object):

    error_state = None
    next_state = None

    def enter(self, context, prev_state):
        pass

    def accept(self, context, event):
        return self.next_state

INITIAL_STATE = State()
ERROR_STATE = State()
FINAL_STATE = State()
State.error_state = ERROR_STATE
State.next_state = FINAL_STATE


class Context(object):
    
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def send(self, msg_id, *args):
        self.dispatcher.send(msg_id, *args)


class Workflow(State):

    name = None

    def __init__(self, intial_state):
        self.state = intial_state

    def enter(self, context, prev_state):
        return self.transition(context, self.state.enter(context, prev_state))

    def accept(self, context, event):
        return self.transition(context, self.state.accept(context, event))
    
    def transition(self, context, state):
        prev_state = self.state
        while state is not None:
            self.state = state
            state = state.enter(context, prev_state)
            prev_state = self.state
        if self.state is ERROR_STATE:
            return ERROR_STATE
        elif self.state is FINAL_STATE:
            return self.next_state
            

# vim: et ts=4 sts=4
