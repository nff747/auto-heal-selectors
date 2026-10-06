import { CLICommands } from './commands';

export function runCLI(argv: string[]): void {
  const args = argv.slice(2);
  const command = args[0] || 'help';

  switch (command) {
    case 'report': {
      const formatIdx = args.indexOf('--format');
      const format = (formatIdx !== -1 && args[formatIdx + 1]) ? (args[formatIdx + 1] as any) : 'markdown';
      const output = CLICommands.report(format);
      console.log(output);
      break;
    }
    case 'clean': {
      const cleaned = CLICommands.clean();
      console.log(cleaned ? 'Cleaned .healer artifacts.' : 'No .healer directory found.');
      break;
    }
    case 'patch': {
      const file = args[1];
      const orig = args[2];
      const healed = args[3];
      if (!file || !orig || !healed) {
        console.error('Usage: auto-heal patch <file> <originalSelector> <healedSelector>');
        process.exit(1);
      }
      const success = CLICommands.patch(file, orig, healed);
      console.log(success ? `Patched ${file} successfully.` : `Failed to patch ${file}.`);
      break;
    }
    case 'help':
    default:
      console.log(`
Auto-Heal Selectors CLI 🤖
Usage:
  npx auto-heal report [--format json|markdown|html]
  npx auto-heal clean
  npx auto-heal patch <file> <original> <healed>
      `);
      break;
  }
}
