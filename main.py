from PyCommon.md_py_common.py_common.cli_framework import CommandLineInterface
from PyCommon.md_py_common.py_common.logging import HoornLogger, LogType, DefaultHoornLogOutput, FileHoornLogOutput, \
	LogDirectoryBuilder

if __name__ == "__main__":
	logger: HoornLogger = HoornLogger(min_level=LogType.DEBUG, outputs=[
		DefaultHoornLogOutput(),
		FileHoornLogOutput(LogDirectoryBuilder.build_log_directory("AI Backend", []), max_logs_to_keep=5)
	])
	cli: CommandLineInterface = CommandLineInterface(logger)

	logger.info("AI Backend successfully started!", separator="AI Backend")

	cli.start_listen_loop()

