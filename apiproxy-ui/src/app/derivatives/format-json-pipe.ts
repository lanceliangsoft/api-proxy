import { Pipe, PipeTransform } from '@angular/core';
import { formatJson, isJson } from '../utils/utils';

@Pipe({
  name: 'formatJson',
})
export class FormatJsonPipe implements PipeTransform {
  transform(value: unknown, ...args: unknown[]): unknown {
    if (args.length > 0 && args[0] && typeof(value) === 'string' && isJson(value as string)) {
      return formatJson(value, true);
    }
    return value;
  }
}
