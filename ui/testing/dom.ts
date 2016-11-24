import { Component } from '@angular/core';
import { ComponentFixture } from '@angular/core/testing';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';


export class DOMHelper {
  fixture: ComponentFixture<Component>;
  element: HTMLElement;

  public get isVisible(): boolean {
    return !!this.element;
  }

  public get innerText(): string {
    if (!this.element) {
      throw 'No element selected!';
    }
    return this.element.textContent;
  }

  public get value(): string {
    if (!this.element) {
      throw 'No element selected!';
    }
    return (this.element as HTMLInputElement).value;
  }

  constructor(componentFixture: ComponentFixture<Component>) {
    this.fixture = componentFixture;
  }


  select(css: string): DOMHelper {
     this.element = this.fixture.nativeElement.querySelector(css);
     return this;
  }

  parent(): DOMHelper {
    this.element = this.element.parentElement;
    return this;
  }

  setValue(value: string): Promise<any> {
    if (this.isVisible) {
      console.log((this.element as HTMLInputElement).value);
      (this.element as HTMLInputElement).value = value;
      this.element.dispatchEvent(new Event('input'));
      this.fixture.detectChanges();
      return this.fixture.whenStable();
    }
    throw 'No element selected';
  }

  click(css?: string): DOMHelper {
    if (!css && !this.isVisible) {
      throw 'No element to click selected';
    }
    if (css) {
      return this.select(css).click();
    }

    (this.element as HTMLButtonElement).click();
    return this;
  }

  then(f: Function): any {
    let result = f.call(this);
    return result ? result : this;
  }

  modal(): DOMHelper {
    return this.select('.modal');
  }
};