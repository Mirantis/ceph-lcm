import { Component, Input } from '@angular/core';

@Component({
  selector: 'modal',
  template: `
<div class="modal fade" [id]="id" tabindex="-1" role="dialog" aria-hidden="true">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        <h4>{{title}}</h4>
      </div>
      <ng-content select=".modal-body"></ng-content>
      <ng-content select=".modal-footer"></ng-content>
    </div>
  </div>
</div>
`
})
export class Modal {
  @Input() id: string = 'modal';
  @Input() title: string = '';

  show(id: string = 'modal') {
    $('#' + id).modal('show');
  }

  close(id: string = 'modal') {
    $('#' + id).modal('hide');
  }
}