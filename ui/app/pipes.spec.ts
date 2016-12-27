import { Key, Keys, TrimBy, DateTime, JSONString, Index, Deparametrize, Deprefix } from './pipes';

describe('Key pipe', () => {
  let pipe = new Key();

  it('returns object\'s existing property by key', () => {
    expect(pipe.transform({a: 1}, 'a')).toBe(1);
  })

  it('returns object\'s non-existing property by key as default', () => {
    expect(pipe.transform(undefined, 'any_key')).toEqual([]);
  })
});

describe('Keys pipe', () => {
  let pipe = new Keys();

  it('returns keys of the given object as an array', () => {
    expect(pipe.transform({a: 1, c: 2, ee: true})).toEqual(['a', 'c', 'ee']);
  })
});

describe('TrimBy pipe', () => {
  let pipe = new TrimBy();

  it('trims long string by the limit', () => {
    expect(pipe.transform('Looooong text', 2)).toBe('Lo...');
  })

  it('leaves short strings unchanged', () => {
    expect(pipe.transform('Short', 10)).toBe('Short');
  })
});

// Commented out as depends on the timezone
// describe('DateTime pipe', () => {
//   let pipe = new DateTime();

//   it('returns formatted date being given a timestamp', () => {
//     expect(pipe.transform(1478608520)).toBe('08/11/2016 15:35:20');
//   });
// });

describe('JSON String pipe', () => {
  let pipe = new JSONString();

  it('transforms given object into a json', () => {
    expect(pipe.transform({a: 1})).toBe('{\n  "a": 1\n}');
  })
});

describe('Index pipe', () => {
  let pipe = new Index();

  it('returns element by numeric index', () => {
    expect(pipe.transform(['a', 2, true], 2)).toBeTruthy();
  });

  it('if index is greater than length - first element should be returned', () => {
    expect(pipe.transform([4, 2], 5)).toBe(4);
  });

  it('treats non-array sources as array of a single element', () => {
    expect(pipe.transform('base', 3)).toBe('base');
  });
});

describe('Deparametrize pipe', () => {
  let pipe = new Deparametrize();

  it('splits source by _, uppercase the first word and glues them back with " "', () => {
    expect(pipe.transform('user_first_name')).toBe('User first name');
  });
});

describe('Deprefix pipe', () => {
  let pipe = new Deprefix();

  it('removes prefix from source and swaps "_" with " "', () => {
    expect(pipe.transform('angular_framework_use', 'angular')).toBe('framework use');
  });

  it('removes only the first occurence of the prefix', () => {
    expect(pipe.transform('home_sweet_home', 'home')).toBe('sweet home');
  });
});