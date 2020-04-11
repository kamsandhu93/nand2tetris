class VMWriter:

    def __init__(self, output_file: str) -> None:
        self._file_name = output_file
        self._output_list = []

    def write_push(self, segment: str, index: int) -> None:
        self._output_list.append(f'push {segment} {index}')

    def write_pop(self, segment: str, index: int) -> None:
        self._output_list.append(f'pop {segment} {index}')

    def write_arithmetic(self, command: str) -> None:
        if command not in []:
            raise Exception(f'Invalid arithmetic command: {command}')
        self._output_list.append(command)

    def write_label(self, label: str) -> None:
        self._output_list.append(f'label {label}')

    def write_go_to(self, label: str) -> None:
        self._output_list.append(f'if-goto {label}')

    def write_if(self, label: str) -> None:
        self._output_list.append(f'if {label}')

    def write_call(self, name: str, n_args: int) -> None:
        self._output_list.append(f'call {name} {n_args}')

    def write_function(self, name: str, n_locals: int) -> None:
        self._output_list.append(f'function {name} {n_locals}')

    def write_return(self):
        self._output_list.append('return')

    def close(self):
        with open(self._file_name, 'w') as f:
            f.writelines(self._output_list)
            