import * as _ from 'lodash';
import 'bootstrap';
import { Component, Directive, Input, Output, EventEmitter,
  AfterViewInit, HostListener, QueryList, ContentChild, ContentChildren } from '@angular/core';


// Filtering criterion
@Directive({
  selector: '[criterion]'
})
export class Criterion {
  @Output() onChange = new EventEmitter();
  @Output() reset = new EventEmitter();
  offset = 0;
}

export class BaseCriterion implements AfterViewInit{
  @Input() title: string = '';
  @Input() target: string = '';
  @ContentChild(Criterion) criterion: Criterion;
  value: string;

  ngAfterViewInit() {
    this.criterion.reset.subscribe(() => {
      this.value = '';
      this.handleUpdate('');
    });
  }

  getCss() {
    return {
      'col-xs-3': true,
      ['col-xs-offset-' + this.criterion.offset]: this.criterion.offset > 0
    };
  }

  buildCondition(newValue: string): any {
    return {
      [this.target]: {'eq': newValue}
    };
  }

  handleUpdate(newValue: string) {
    this.criterion.onChange.emit(
      newValue === '' ? {remove: this.target} : this.buildCondition(newValue)
    );
  }
}

@Component({
  selector: 'search',
  templateUrl: './app/templates/criteria/search.html'
})
export class SearchCriterion extends BaseCriterion {
  buildCondition(newValue: string) {
    return {
      [this.target]: {regexp: newValue}
    };
  }
}

@Component({
  selector: 'choice',
  templateUrl: './app/templates/criteria/choice.html'
})
export class ChoiceCriterion extends BaseCriterion {
  @Input() values: any[] = [];
}

// Filter control
@Component({
  selector: 'filter',
  templateUrl: './app/templates/filter.html'
})
export class Filter implements AfterViewInit  {
  @Output() onChange = new EventEmitter();
  @ContentChildren(Criterion) criteria: QueryList<Criterion>;
  query: Object = {};
  timeout: number;

  ngAfterViewInit() {
    this.criteria.forEach((criterion: Criterion, index) => {
      criterion.onChange.subscribe((criterionValue: any) => this.criterionUpdated(criterionValue));
      if (index === 1) criterion.offset = this.getCriteriaOffset();
    });
  }

  getCriteriaOffset() {
    let criteriaCount = this.criteria.length;
    return 8 - (criteriaCount - 1) * 3;
  }

  reset() {
    this.criteria.forEach((criterion: Criterion) => criterion.reset.emit());
  }

  isQuerySet() {
    return _.isEmpty(this.query);
  }

  criterionUpdated(criterion: any) {
    if (criterion['remove']) {
      _.unset(this.query, criterion.remove);
    } else {
      _.assign(this.query, criterion);
    }

    if (this.timeout) {
      window.clearTimeout(this.timeout);
    }
    this.timeout = window.setTimeout(() => this.onChange.emit(), 1000);
  }
}
