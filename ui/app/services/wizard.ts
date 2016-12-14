import { Injectable, EventEmitter } from '@angular/core';

@Injectable()
export class WizardService {
  public currentStep = new EventEmitter();
  public model = new EventEmitter();
  public sharedData = {};
  public sharedDataUpdated = new EventEmitter();

  constructor() {}
}