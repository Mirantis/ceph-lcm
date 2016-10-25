"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var core_1 = require('@angular/core');
var forms_1 = require('@angular/forms');
var platform_browser_1 = require('@angular/platform-browser');
var directives_1 = require('./directives');
var pipes_1 = require('./pipes');
var SharedModule = (function () {
    function SharedModule() {
    }
    SharedModule = __decorate([
        core_1.NgModule({
            imports: [
                platform_browser_1.BrowserModule, forms_1.FormsModule
            ],
            declarations: [
                directives_1.Modal, directives_1.Loader, directives_1.Filter, directives_1.Criterion, directives_1.Pager, directives_1.LongData,
                pipes_1.Keys, pipes_1.Key, pipes_1.TrimBy, pipes_1.DateTime, pipes_1.JSONString, pipes_1.Index, pipes_1.Deparametrize, pipes_1.Deprefix
            ],
            exports: [
                directives_1.Modal, directives_1.Loader, directives_1.Filter, directives_1.Criterion, directives_1.Pager, directives_1.LongData,
                pipes_1.Keys, pipes_1.Key, pipes_1.TrimBy, pipes_1.DateTime, pipes_1.JSONString, pipes_1.Index, pipes_1.Deparametrize, pipes_1.Deprefix
            ],
            providers: [
                directives_1.Modal, directives_1.Loader, directives_1.Filter, directives_1.Criterion, directives_1.Pager, directives_1.LongData
            ]
        }), 
        __metadata('design:paramtypes', [])
    ], SharedModule);
    return SharedModule;
}());
exports.SharedModule = SharedModule;
//# sourceMappingURL=shared.module.js.map