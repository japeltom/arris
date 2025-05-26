from PySide6.QtStateMachine import QState, QStateMachine

from util import DotDict

class BaseController:
    """A base class for the controller that sets up the state machine and its
    transitions, but does not perform any actual program logic."""

    def __init__(self, config, context):
        self.config = config
        self.context = context

    def _setup_state_machine(self):
        self.machine = QStateMachine()

        # States.
        root_state = QState()
        root_state.setChildMode(QState.ParallelStates)
        # Notice that the first state in each state group is set as the initial
        # state.
        states = dict(
            group_edited=[
                "not_edited",
                "edited",
            ],
            group_action=[
                "initial",
                "edit_zero_files",
                "edit_one_file",
                "edit_many_files",
            ]
        )
        self.group_states = DotDict({})
        self.states = DotDict({})
        for group_id, states in states.items():
            self.group_states[group_id] = QState(root_state)
            self.states[group_id] = DotDict({state:QState(self.group_states[group_id]) for state in states})
            for n, state in enumerate(states):
                self.states[group_id][state].setObjectName(state)
                if n == 0:
                    # Set initial state.
                    self.group_states[group_id].setInitialState(self.states[group_id][state])

        # Transitions.
        transitions = dict(
            group_edited=dict(
                # source state
                not_edited=[
                    # context.signal, target_state
                    ("event_edit", "edited"),
                ],
                edited=[
                    ("discard_edits", "not_edited"),
                    ("saved_edits", "not_edited"),
                ]
            ),
            group_action=dict(
                initial=[
                    ("update_files", "edit_zero_files"),
                ],
                edit_zero_files=[
                    ("discard_edits", "initial"),
                    ("edit_one_file", "edit_one_file"),
                    ("edit_many_files", "edit_many_files"),
                ],
                edit_one_file=[
                    ("discard_edits", "initial"),
                    ("edit_zero_files", "edit_zero_files"),
                    ("edit_many_files", "edit_many_files"),
                ],
                edit_many_files=[
                    ("discard_edits", "initial"),
                    ("edit_zero_files", "edit_zero_files"),
                    ("edit_one_file", "edit_one_file"),
                ]
            ),
        )
        for group_id, group_transitions in transitions.items():
            for state, transitions in group_transitions.items():
                for context, target_state in transitions:
                    context = getattr(self.context, context)
                    self.states[group_id][state].addTransition(context, self.states[group_id][target_state])

        # State entry actions.
        self.states.group_edited.not_edited.entered.connect(self.enter_not_edited)
        self.states.group_edited.edited.entered.connect(self.enter_edited)
        self.states.group_action.initial.entered.connect(self.enter_initial)
        self.states.group_action.edit_zero_files.entered.connect(self.enter_edit_zero_files)
        self.states.group_action.edit_one_file.entered.connect(self.enter_edit_one_file)
        self.states.group_action.edit_many_files.entered.connect(self.enter_edit_many_files)

        self.machine.addState(root_state)
        self.machine.setInitialState(root_state)
        self.machine.start()

    def get_state(self):
        result = DotDict({})
        for group_id in self.group_states:
            for state in self.states[group_id].values():
                if state in self.machine.configuration():
                    result[group_id] = state.objectName()
                    break
        return result

    def enter_edited(self):
        """Handles the event that the edited state changes to 'edited'."""

        if self.config.general.debug:
            print("State: edited")
        self.app.enter_edited()

    def enter_not_edited(self):
        """Handles the event that the edited state changes to 'not_edited'."""

        if self.config.general.debug:
            print("State: not_edited")
        self.app.enter_not_edited()

    def enter_initial(self):
        """Handles the event that the action state changes to 'initial'."""

        if self.config.general.debug:
            print("State: initial")
        self.context.enter_initial.emit()

    def enter_edit_zero_files(self):
        """Handles the event that the action state changes to
        'edit_zero_files'."""

        if self.config.general.debug:
            print("State: edit_zero_files") 

    def enter_edit_one_file(self):
        """Handles the event that the action state changes to
        'edit_one_file'."""

        if self.config.general.debug:
            print("State: edit_one_file") 

    def enter_edit_many_files(self):
        """Handles the event that the action state changes to
        'edit_many_files'."""

        if self.config.general.debug:
            print("State: edit_many_files") 

