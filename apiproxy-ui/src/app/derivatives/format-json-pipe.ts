import { Pipe, PipeTransform } from '@angular/core';
import { isJson } from '../utils/utils';

@Pipe({
  name: 'formatJson',
})
export class FormatJsonPipe implements PipeTransform {
  transform(value: unknown, ...args: unknown[]): unknown {
    if (args.length > 0 && args[0] && typeof(value) === 'string' && isJson(value as string)) {
      try {
        const obj = JSON.parse(value);
        return JSON.stringify(obj, null, 2);
      } catch(err) {
        console.error(err);
      }
    }
    return value;
  }
}
