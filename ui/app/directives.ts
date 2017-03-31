/**
* Copyright (c) 2016 Mirantis Inc.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
* implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

import { Component, Directive, Input, Output, EventEmitter, ViewChild,
  AfterViewInit, HostListener, ElementRef, ChangeDetectorRef } from '@angular/core';
import { ErrorService } from './services/error';
import * as jQuery from 'jquery';
import * as _ from 'lodash';
import 'bootstrap';
import globals = require('./services/globals');
import { BaseModel } from './models';

// Bootstrap modal methods
@Component({
  selector: 'modal',
  templateUrl: './app/templates/bootstrap_modal.html'
})
export class Modal {
  @Input() id: string = 'modal';
  @Input() title: string = '';
  @Input() isLarge: boolean = false;

  errors: {error: string, message: string}[] = [];

  constructor(private error: ErrorService) {
    error.errorHappened.subscribe((error: any) => this.addError(error));
  }

  show(id: string = 'modal') {
    jQuery('#' + id).modal({backdrop: 'static', show: true});
  }

  isExpanded() {
    return jQuery('#modal-dialog').hasClass('modal-lg');
  }

  toggleLarge() {
    jQuery('#modal-dialog').toggleClass('modal-lg');
  }

  close(id: string = 'modal') {
    jQuery('#' + id).modal('hide');
    if (this.isExpanded() !== this.isLarge) {
      setTimeout(this.toggleLarge, 500);
    }
  }

  addError(error: any) {
    if (_.isEmpty(error)) {
      this.errors = [];
    } else {
      this.errors.push(error);
    }
  }

  dismissErrors() {
    this.errors = [];
  }

  isOpened(id: string = 'modal'): boolean {
    return jQuery('#' + id).is(':visible');
  }
};

// Rotating decapod loading indicator
@Component({
  selector: 'loader',
  templateUrl: './app/templates/loader.html'
})
export class Loader {};

// Pagination
@Component({
  selector: 'pager',
  templateUrl: './app/templates/pager.html'
})
export class Pager {
  visiblePages = 5;
  @Input() pagingData: {total: number, per_page: number, page: number} = null;
  @Input() isHidden: boolean = false;
  @Output() onChange  = new EventEmitter();

  public get page(): number {
    return +this.pagingData.page || 1;
  }

  public get perPage(): number {
    return +this.pagingData.per_page || 25;
  }

  getVisiblePages(): number[] {
    let totalPages = Math.ceil(this.pagingData.total / this.pagingData.per_page);
    if (this.page > totalPages) {
      this.switchPage(1);
    }
    let start = this.pagingData.page - Math.round(this.visiblePages / 2);
    if (start < 1) {
      start = 1;
    };
    let finish = start + this.visiblePages;
    if (finish > totalPages) {
      finish = totalPages;
    }
    return _.range(start, finish + 1);
  }

  switchPage(page: number) {
    this.onChange.emit(page);
  }

  getPageItems(allItems: BaseModel[]): BaseModel[] {
    return _.slice(allItems, (this.page - 1) * this.perPage, this.perPage);
  }
}

// Long data view
@Component({
  selector: 'longdata',
  template: `<a (click)="expand()" *ngIf="isCollapsed()">{{'{...}'}}</a><span *ngIf="!isCollapsed()"><ng-content></ng-content></span>`
})
export class LongData {
  @Input() key: string;
  @Input() max: number = 50;
  @Input() data: Object = '';
  length: number = 0;

  ngOnInit() {
    this.length = JSON.stringify(this.data).length;
  }

  isCollapsed(): boolean {
    return this.length > this.max && _.get(globals.tempStorage, this.key, true);
  }

  expand() {
    globals.tempStorage[this.key] = false;
  }
}

@Directive({
  selector: '[confirmedClick]'
})
export class Confirmation {
  static bus = new EventEmitter();

  @Input() confirmation = 'Are you sure?';
  @Output() confirmedClick = new EventEmitter();
  @HostListener('click', ['$event']) onClick(e: MouseEvent) {
    Confirmation.bus.emit({confirmation: this.confirmation, callback: this.confirmedClick});
  }
}

@Directive({
  selector: '[submits]'
})
export class Submitter {
  @Input('submits') submitterRef: string|string[];
  @HostListener('keyup', ['$event']) onKeyUp(e: KeyboardEvent) {
    if (e.keyCode === 13) {
      this.clicker.emit();
    }
  }
  clicker = new EventEmitter();
  constructor(cdr: ChangeDetectorRef) {
    this.clicker.subscribe(() => {
      _.some(
        _.flatten([this.submitterRef]),
        (submittee: string) => {
          let element = jQuery(submittee + ':enabled')[0];
          if (!_.isEmpty(element)) {
            element.click();
            cdr.detectChanges();
            return true;
          }
          return false;
        }
      );
    });
  }
}