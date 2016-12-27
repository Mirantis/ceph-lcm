import { Component } from '@angular/core';
import { ComponentFixture } from '@angular/core/testing';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';


export class DOMHelper {
  fixture: ComponentFixture<Component>;
  element: HTMLElement;

  private checkElement() {
    if (!this.element) {
      throw 'No element selected!';
    }
  }

  public get isVisible(): boolean {
    return !!this.element;
  }

  public get isDisabled(): boolean {
    return (this.element as HTMLInputElement).disabled;
  }

  public get innerText(): string {
    this.checkElement();
    return this.element.textContent;
  }

  public get innerHTML(): string {
    this.checkElement();
    return this.element.innerHTML;
  }

  public get className(): string {
    this.checkElement();
    return this.element.className;
  }

  public get value(): string {
    this.checkElement();
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
    this.checkElement();
    this.element = this.element.parentElement;
    return this;
  }

  setValue(value: string): Promise<any> {
    this.checkElement();
    (this.element as HTMLInputElement).value = value;
    this.element.dispatchEvent(new Event('input'));
    this.fixture.detectChanges();
    return this.fixture.whenStable();
  }

  click(css?: string): DOMHelper {
    if (!css && !this.isVisible) {
      throw 'No element selected to click on';
    }
    if (css) {
      return this.select(css).click();
    }

    (this.element as HTMLButtonElement).click();
    this.fixture.detectChanges();
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